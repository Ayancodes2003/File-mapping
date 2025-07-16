import json
from collections import defaultdict

INPUT = "data/reference_map.json"
OUTPUT = "data/inverted_map.json"

with open(INPUT, "r") as f:
    reference_map = json.load(f)

# Build: case_id → list of files that cite it
inverted = defaultdict(list)

for source_file, info in reference_map.items():
    for ref, resolved in info.get("resolved", {}).items():
        if resolved:
            inverted[ref].append(source_file)

# Save
with open(OUTPUT, "w") as f:
    json.dump(inverted, f, indent=2)

print("✅ Inverted map created → data/inverted_map.json")
