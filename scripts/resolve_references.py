from rapidfuzz import process, fuzz
import os, json
import pandas as pd
from normalize import normalize_citation

REFERENCE_FILE = "data/reference_map.json"
PDF_DIR = "data/raw_pdfs"
METADATA_FILE = "data/metadata.csv"

# Load reference map
with open(REFERENCE_FILE, "r") as f:
    reference_map = json.load(f)

# Build filename index
pdf_filenames = {f.replace(".pdf", "").upper(): f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")}
pdf_keys = list(pdf_filenames.keys())

# Load metadata
metadata_index = {}
metadata_keys = []
if os.path.exists(METADATA_FILE):
    try:
        df = pd.read_csv(METADATA_FILE)
        if not df.empty:
            df["case_id"] = df["case_id"].astype(str).str.upper()
            df["filename"] = df["filename"].astype(str)
            metadata_index = dict(zip(df["case_id"], df["filename"]))
            metadata_keys = list(metadata_index.keys())
    except pd.errors.EmptyDataError:
        print("⚠️ metadata.csv is empty")

def resolve_best_match(ref: str, threshold=90):
    # Direct metadata match
    if ref in metadata_index:
        return metadata_index[ref]

    # Fuzzy match against metadata
    match_meta, score_meta, _ = process.extractOne(ref, metadata_keys, scorer=fuzz.ratio)
    if score_meta >= threshold:
        return metadata_index[match_meta]

    # Fuzzy match against filenames
    match_file, score_file, _ = process.extractOne(ref, pdf_keys, scorer=fuzz.ratio)
    if score_file >= threshold:
        return pdf_filenames[match_file]

    return None

# Resolve
for source_file, info in reference_map.items():
    resolved = {}
    for ref in info["references"]:
        ref_norm = normalize_citation(ref)
        if not ref_norm:
            resolved[ref] = None
            continue
        match = resolve_best_match(ref_norm)
        resolved[ref] = match
    reference_map[source_file]["resolved"] = resolved

# Save updated map
with open(REFERENCE_FILE, "w") as f:
    json.dump(reference_map, f, indent=2)

print("✅ Enhanced reference resolution complete.")
