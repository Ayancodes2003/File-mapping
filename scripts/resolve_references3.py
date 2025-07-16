import os
import json
import re
import pandas as pd
from rapidfuzz import process, fuzz
from normalize import normalize_citation
from llm_resolver import resolve_with_semantic_match
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PDF_DIR = "data/raw_pdfs"
METADATA_FILE = "data/metadata.csv"
REFERENCE_FILE = "data/reference_map.json"
CASE_INDEX_FILE = "data/case_index.json"
OUT_FILE = "data/reference_map.json"

# --- Load metadata ---
metadata_index = {}
if os.path.exists(METADATA_FILE):
    df = pd.read_csv(METADATA_FILE, dtype=str)
    df["case_id"] = df["case_id"].str.upper()
    df["filename"] = df["filename"].astype(str)
    metadata_index = dict(zip(df["case_id"], df["filename"]))

# Reverse: filename → own case_id
file_case_index = {v: k for k, v in metadata_index.items()}
metadata_keys = list(metadata_index.keys())

# --- Load PDF filenames ---
pdf_filenames = {
    f.replace(".pdf", "").upper(): f
    for f in os.listdir(PDF_DIR)
    if f.endswith(".pdf")
}
pdf_keys = list(pdf_filenames.keys())

# --- Load case index (case_id → party info) ---
with open(CASE_INDEX_FILE) as f:
    case_index = json.load(f)

# --- Load reference map ---
with open(REFERENCE_FILE) as f:
    reference_map = json.load(f)

# --- Resolver function ---
def resolve_best_match(ref_id):
    if ref_id in metadata_index:
        return metadata_index[ref_id]
    
    # Fuzzy match on metadata
    match, score, _ = process.extractOne(ref_id, metadata_keys, scorer=fuzz.ratio)
    if score >= 90:
        return metadata_index[match]
    
    # Fuzzy match on filenames
    match2, score2, _ = process.extractOne(ref_id, pdf_keys, scorer=fuzz.ratio)
    if score2 >= 90:
        return pdf_filenames[match2]
    
    return None

# --- Main loop ---
for source_file, info in reference_map.items():
    resolved = {}
    own_case_id = normalize_citation(file_case_index.get(source_file, ""))

    for ref in info.get("references", []):
        ref_norm = normalize_citation(ref)

        # Skip self-citation
        if own_case_id and ref_norm == own_case_id:
            continue

        match = resolve_best_match(ref_norm)

        # Fallback to semantic match if unresolved
        if not match and ref:
            match = resolve_with_semantic_match(ref, case_index)

        resolved[ref] = match

    reference_map[source_file]["resolved"] = resolved

# --- Save output ---
with open(OUT_FILE, "w") as f:
    json.dump(reference_map, f, indent=2)

print(f"✅ Updated reference map saved to {OUT_FILE}")
