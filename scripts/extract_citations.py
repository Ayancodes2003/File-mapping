import os, re, json
from tqdm import tqdm
from normalize import normalize_citation

INPUT_DIR = "data/extracted_texts"
OUTPUT_FILE = "data/reference_map.json"

CITATION_PATTERN = r"\b(?:CWP|FAO|CRP|SLP|LPA|RFA|RSA|WP|OA|MA|SLA)\s+No\.?\s*\d+\s*(?:of|/)\s*\d{4}\b"

reference_map = {}

for file in tqdm(os.listdir(INPUT_DIR)):
    if not file.endswith(".txt"): continue
    with open(os.path.join(INPUT_DIR, file), encoding="utf-8") as f:
        text = f.read()
    matches = re.findall(CITATION_PATTERN, text)
    normalized = list({normalize_citation(m) for m in matches if normalize_citation(m)})
    reference_map[file.replace(".txt", ".pdf")] = {
        "references": normalized,
        "resolved": {}  # to be filled later
    }

with open(OUTPUT_FILE, "w") as f:
    json.dump(reference_map, f, indent=2)
