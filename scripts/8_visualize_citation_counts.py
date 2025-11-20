import json
import matplotlib.pyplot as plt

with open("../citers/citing_hmlv.json") as f:
    citing = json.load(f)

counts = {hmlv: len(citers) for hmlv, citers in citing.items()}

plt.figure(figsize=(14,6))
plt.bar(counts.keys(), counts.values())
plt.xticks(rotation=90)
plt.title("Citation Count per HMLV Paper")
plt.ylabel("# of Citing Documents")
plt.tight_layout()
plt.show()
