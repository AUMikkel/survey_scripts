import json
import itertools
import pandas as pd

with open("../citers/citing_hmlv.json") as f:
    citing = json.load(f)

# Build reverse index: review → set of HMLV papers
review_to_set = {}

for hmlv_id, citers in citing.items():
    for citer in citers:
        # Filter to only include reviews
        if citer.get("type") != "Review":
            #print(f"Skipping non-review citer: {citer.get('scopus_id')} of type {citer.get('type')}")
            continue
        
        r = citer["scopus_id"]
        review_to_set.setdefault(r, set()).add(hmlv_id)

# Compute pairwise overlaps
rows = []
for r1, r2 in itertools.combinations(review_to_set.keys(), 2):
    overlap = len(review_to_set[r1] & review_to_set[r2])
    if overlap > 0:
        rows.append({"review1": r1, "review2": r2, "overlap": overlap})

df = pd.DataFrame(rows)
df.to_csv("review_overlap.csv", index=False)

print(df.head())
