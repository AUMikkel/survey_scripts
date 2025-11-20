import json
import glob

files = sorted(glob.glob("./rfs/review_refs_batch_*.json"))
combined = {}

for f in files:
    with open(f, "r") as infile:
        data = json.load(infile)
        combined.update(data)

with open("all_reviews_refs.json", "w") as outfile:
    json.dump(combined, outfile, indent=2)

print(f"✅ Combined {len(files)} files into all_reviews_refs.json with {len(combined)} reviews total.")
