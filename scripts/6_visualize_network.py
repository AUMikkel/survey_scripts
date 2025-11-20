import json
import networkx as nx
import matplotlib.pyplot as plt

# Load data
with open("../citers/citing_hmlv.json") as f:
    citing = json.load(f)

G = nx.Graph()

# Add edges
for hmlv_id, citers in citing.items():
    for citer in citers:
        # Filter to only include reviews
        if citer.get("type") != "Review":
            #print(f"Skipping non-review citer: {citer.get('scopus_id')} of type {citer.get('type')}")
            continue
        
        review = citer["scopus_id"]

        G.add_node(review, bipartite=0)
        G.add_node(hmlv_id, bipartite=1)
        G.add_edge(review, hmlv_id)

# Draw
plt.figure(figsize=(16, 10))
pos = nx.spring_layout(G, k=0.35)

nx.draw(G, pos,
        node_size=30,
        width=0.3,
        with_labels=False)

plt.title("Review ↔ HMLV Citation Network")
plt.show()
