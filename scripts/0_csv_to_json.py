import pandas as pd
import json
import re

df = pd.read_csv("hmlv_dss_results.csv")

reviews = []
for _, row in df.iterrows():
    scopus_id = re.sub(r"SCOPUS_ID:?", "", str(row.get("EID", ""))).strip()
    reviews.append({
        "title": str(row.get("Title", "")).strip(),
        "doi": str(row.get("DOI", "")).strip(),
        "scopus_id": scopus_id
    })

with open("hmlv_dss_results.json", "w") as f:
    json.dump(reviews, f, indent=2)

print(f"💾 Saved {len(reviews)} reviews to hmlv_dss_results.json")
