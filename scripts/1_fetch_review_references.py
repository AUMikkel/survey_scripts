import requests
import os
import json
import time

# ======= SETTINGS =======
API_KEY = os.getenv("SCOPUS_API_KEY")
INPUT_FILE = "review_batch_1.json"
OUTPUT_FILE = "./rfs/review_refs_batch_5.json"

# Choose which slice of reviews to process
START_INDEX = 100     # inclusive
END_INDEX = 111      # exclusive (so this runs 100–110)
# =========================

headers = {
    "Accept": "application/json",
    "X-ELS-APIKey": API_KEY,
    "X-ELS-ResourceVersion": "XOCS"
}

def fetch_references(scopus_id):
    """Fetch reference list for a given Scopus ID, with error handling."""
    clean_id = str(scopus_id).replace("SCOPUS_ID:", "").replace("2-s2.0-", "").strip()
    url = f"https://api.elsevier.com/content/abstract/scopus_id/{clean_id}?view=REF"

    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": API_KEY,
        "X-ELS-ResourceVersion": "XOCS"
    }

    # Retry up to 3 times if the API glitches
    for attempt in range(3):
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            break
        print(f"⚠️ Error {r.status_code} for {clean_id}, retry {attempt+1}/3 in 5s...")
        time.sleep(5)
    else:
        print(f"❌ Failed to fetch {clean_id} after 3 attempts.")
        return []

    try:
        data = r.json()
    except Exception:
        print(f"⚠️ Failed to parse JSON for {clean_id}")
        return []

    response = data.get("abstracts-retrieval-response")
    if not response:
        print(f"⚠️ No 'abstracts-retrieval-response' for {clean_id}")
        return []

    refs_data = response.get("references")
    if not refs_data:
        print(f"ℹ️ No references found for {clean_id}")
        return []

    refs = refs_data.get("reference", [])
    out = []
    for ref in refs:
        ref_info = ref.get("ref-info", {}).get("ref-publicationinfo", {})
        out.append({
            "title": ref_info.get("title", ""),
            "doi": ref_info.get("doi", ""),
            "scopus_id": ref.get("scopus-id", "")
        })

    return out



def main():
    with open(INPUT_FILE, "r") as f:
        reviews = json.load(f)

    total_reviews = len(reviews)
    print(f"📚 Found {total_reviews} reviews in {INPUT_FILE}")

    # Clamp indices so you don’t go out of range
    start = max(0, START_INDEX)
    end = min(END_INDEX, total_reviews)
    batch = reviews[start:end]
    print(f"🚀 Processing reviews {start}–{end-1} ({len(batch)} total)\n")

    # Load or initialize previous results
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            all_refs = json.load(f)
    else:
        all_refs = {}

    for i, rev in enumerate(batch, start=start + 1):
        sid = str(rev.get("scopus_id", "")).strip()
        if not sid:
            continue

        if sid in all_refs:
            print(f"[{i}] Skipping {sid} (already fetched)")
            continue

        print(f"[{i}] Fetching references for {sid} ...")
        refs = fetch_references(sid)
        all_refs[sid] = refs

        # Save progress after each paper
        with open(OUTPUT_FILE, "w") as f:
            json.dump(all_refs, f, indent=2)

        print(f"   ✅ {len(refs)} references saved ({len(all_refs)} total)")
        time.sleep(1.5)  # polite delay

    print(f"\n🎉 Done! Processed {len(batch)} reviews ({start}-{end-1}) and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

