import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# Load your citing data
with open("../citers/citing_hmlv.json", "r") as f:
    citing = json.load(f)

# Use a list to store rows and a set to avoid duplicates
rows = []
seen = set()   # to avoid adding same review twice
rows_dicrtionary = {}

for hmlv_id, citers in citing.items():
    for citer in citers:

        # Only include reviews
        if citer.get("type") != "Review":
            continue

        review_id = citer.get("scopus_id")

        if review_id in rows_dicrtionary:
            rows_dicrtionary[review_id]["HMLV_IDs"].append(hmlv_id)
        else:
            rows_dicrtionary[review_id] = {
                "HMLV_IDs": [hmlv_id],
                "Review_ID": review_id,
                "Title": citer.get("title")
            }

def flatten_hmlv_ids(hmlv_ids):
    return ", ".join(hmlv_ids)

def flatten_rows(rows_dicrtionary):
    flattened_rows = []
    for review_id, data in rows_dicrtionary.items():
        flattened_rows.append({
            "Review_ID": data["Review_ID"],
            "Title": data["Title"],
            "HMLV_IDs": flatten_hmlv_ids(data["HMLV_IDs"]),
            "Count_HMLV_Citations": len(data["HMLV_IDs"])
        })
    return flattened_rows


def save_rows_to_csv(rows, output_file, path=None):
    rows = flatten_rows(rows)
    df = pd.DataFrame(rows)
    if path:
        output_file = f"{path}/{output_file}"
    df.to_excel(output_file, index=False)
    print(f"Saved {len(rows)} rows to {output_file}")


def main():
    # Do something with rows
    output_file = "review_titles.xlsx"
    path = "../citers/"
    save_rows_to_csv(rows_dicrtionary, output_file, path)

if __name__ == "__main__":
    main()