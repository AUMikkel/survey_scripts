import pandas as pd
import json
import glob
import os

# --- 1️⃣  Input files ---------------------------------------------------------
CSV_FILE = "hmlv_dss_results.csv"        # Your exported HMLV + DSS papers
REVIEW_PATH = "./rfs/"                   # Folder with review_refs_batch_*.json
OUTPUT_FILE = "matched_papers.json"

# --- 2️⃣  Load HMLV + DSS dataset --------------------------------------------
df = pd.read_csv(CSV_FILE)
df.columns = [c.strip().lower() for c in df.columns]

# Find EID column automatically (Scopus ID)
eid_col = next((c for c in df.columns if "eid" in c or "scopus" in c), None)
if not eid_col:
    raise ValueError("No EID/Scopus ID column found in CSV!")

# Normalize Scopus IDs (remove '2-s2.0-' etc.)
df["clean_id"] = df[eid_col].astype(str).str.replace("2-s2.0-", "").str.replace("SCOPUS_ID:", "").str.strip()

print(f"✅ Loaded {len(df)} HMLV+DSS papers from CSV")

# --- 3️⃣  Load all review reference JSON files -------------------------------
review_files = glob.glob(os.path.join(REVIEW_PATH, "review_refs_batch_*.json"))
if not review_files:
    print("⚠️ No review reference files found. Check your REVIEW_PATH.")
    exit()

print(f"📂 Found {len(review_files)} review reference files")

ref_to_reviews = {}  # Map: cited_paper_id -> list of review_ids that cite it
ref_ids = set()

for file in review_files:
    with open(file, "r") as f:
        data = json.load(f)
        for review_id, refs in data.items():
            for r in refs:
                rid = str(r.get("scopus_id", "")).replace("2-s2.0-", "").strip()
                if rid:
                    ref_ids.add(rid)
                    ref_to_reviews.setdefault(rid, []).append(review_id)

print(f"📚 Loaded {len(ref_ids)} unique cited Scopus IDs from all reviews")

# --- 4️⃣  Match review references to HMLV+DSS papers -------------------------
topic_ids = set(df["clean_id"])
matches = topic_ids.intersection(ref_ids)
print(f"🎯 Found {len(matches)} HMLV+DSS papers cited in at least one review")

# --- 5️⃣  Build result list ---------------------------------------------------
matched_rows = []
for _, row in df.iterrows():
    cid = str(row["clean_id"])
    if cid in matches:
        matched_rows.append({
            "title": row.get("title", ""),
            "eid": row.get(eid_col, ""),
            "doi": row.get("doi", ""),
            "reviews_that_cite": ref_to_reviews.get(cid, [])
        })

# --- 6️⃣  Save to JSON --------------------------------------------------------
with open(OUTPUT_FILE, "w") as f:
    json.dump(matched_rows, f, indent=2)

print(f"💾 Saved {len(matched_rows)} matched papers to {OUTPUT_FILE}")
