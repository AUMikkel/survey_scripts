import requests
import os
import urllib.parse

# --- 1️⃣  Your Elsevier API key -----------------------------------------------
API_KEY = os.getenv("SCOPUS_API_KEY")  # safer
# or paste directly (not recommended):
# API_KEY = "YOUR_API_KEY_HERE"

# --- 2️⃣  Your Scopus search query -------------------------------------------
query = '''
TITLE-ABS-KEY(hmlv OR "high mix low volume" OR "high-mix low-volume" OR
"low volume high mix" OR "high variety low volume" OR "make-to-order" OR
mto OR "small batch" OR "custom manufacturing" OR "mass customization" OR
"job shop" OR "configure-to-order" OR cto OR "short production runs")
AND TITLE-ABS-KEY("manufact*" OR "production" OR "industr*" OR "Industry 4.0")
AND TITLE-ABS-KEY("Decision Support" OR "Decision-support" OR
"Decision Support System" OR "DSS" OR "Decision Making")
AND PUBYEAR > 2017 AND PUBYEAR < 2025
AND (SUBJAREA(ENGI) OR SUBJAREA(COMP))
AND (DOCTYPE(ar) OR DOCTYPE(cp))
AND LANGUAGE(english)
'''

# --- 3️⃣  Encode and build request URL ----------------------------------------
encoded_query = urllib.parse.quote(query)
base_url = "https://api.elsevier.com/content/search/scopus"
params = f"?query={encoded_query}&count=24&httpAccept=application/json" #25 results per page
url = base_url + params
headers = {"Accept": "application/json", "X-ELS-APIKey": API_KEY}

# --- 4️⃣  Request results ------------------------------------------------------
print("🔍 Querying Scopus API ...")
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("❌ Error:", response.status_code, response.text)
    exit()

data = response.json()

# --- 5️⃣  Parse and display results ------------------------------------------
entries = data.get("search-results", {}).get("entry", [])
if not entries:
    print("No results found.")
    exit()

print(f"✅ Found {len(entries)} papers on this page.\n")

review_count = 0
for e in entries:
    title = e.get("dc:title", "N/A")
    year = e.get("prism:coverDate", "N/A")[:4]
    doi = e.get("prism:doi", "N/A")
    subtype = e.get("subtypeDescription", "")
    if "Review" in subtype or "Survey" in title:
        review_count += 1
        print(f"🧾 Review/Survey {review_count}: {title} ({year})")
        print(f"   DOI: {doi}")
        print(f"   Type: {subtype}")
        print()

print(f"📊 Total review/survey papers found: {review_count}")
