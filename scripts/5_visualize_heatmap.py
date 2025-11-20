import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load your citing data
with open("../citers/citing_hmlv.json", "r") as f:
    citing = json.load(f)

# Flatten: build rows = reviews, columns = HMLV papers
rows = []

for hmlv_id, citers in citing.items():
    #print(f"Processing HMLV paper: {hmlv_id} with {len(citers)} citers")
    for citer in citers:
        # Filter to only include reviews
        if citer.get("type") != "Review":
            #print(f"Skipping non-review citer: {citer.get('scopus_id')} of type {citer.get('type')}")
            continue

        rows.append({
            "review_id": citer["scopus_id"],
            "hmlv_id": hmlv_id
        })
        #print(f"Added review {citer['scopus_id']} citing HMLV paper {hmlv_id}")


df = pd.DataFrame(rows)


# Pivot to matrix
matrix = df.pivot_table(index="review_id", columns="hmlv_id", aggfunc=len, fill_value=0)

print(matrix.shape)
print(matrix.sum().sum())  # total number of citations

fig = px.imshow(matrix,
                 color_continuous_scale="Blues",
                 aspect="auto")
fig.show()

# Heatmap
#plt.figure(figsize=(14, 8))
#sns.heatmap(matrix, cmap="Blues", cbar=True, vmin=0, vmax=1)
#plt.title("Which Reviews Cite Which HMLV Papers")
#plt.xlabel("HMLV Paper")
#plt.ylabel("Review")
#plt.tight_layout()
#plt.show()
