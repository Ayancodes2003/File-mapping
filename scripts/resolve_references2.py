import os, json
import pandas as pd
from normalize import normalize_citation
from rapidfuzz import process, fuzz

REFERENCE_FILE = "data/reference_map.json"
PDF_DIR = "data/raw_pdfs"
METADATA_FILE = "data/metadata.csv"

# Load reference map
with open(REFERENCE_FILE, "r") as f:
    reference_map = json.load(f)

# Index actual PDF filenames
pdf_filenames = {f.replace(".pdf", "").upper(): f
                 for f in os.listdir(PDF_DIR) if f.endswith(".pdf")}
pdf_keys = list(pdf_filenames)

# Load metadata
metadata_index = {}        # case_id → filename
file_case_index = {}       # filename → case_id
metadata_keys = []

if os.path.exists(METADATA_FILE):
    try:
        df = pd.read_csv(METADATA_FILE, dtype=str)
        df["case_id"] = df["case_id"].str.upper()
        df["filename"] = df["filename"].astype(str)
        metadata_index = dict(zip(df["case_id"], df["filename"]))
        file_case_index = {v: k for k, v in metadata_index.items()}
        metadata_keys = list(metadata_index.keys())
    except pd.errors.EmptyDataError:
        print("⚠️ metadata.csv is empty. Only filename matching will be used.")
else:
    print("⚠️ metadata.csv not found. Only filename matching will be used.")

# Fuzzy matching function
def resolve_best_match(ref: str, threshold=90):
    if ref in metadata_index:
        return metadata_index[ref]

    # fuzzy metadata match
    match_meta, score_meta, _ = process.extractOne(ref, metadata_keys, scorer=fuzz.ratio)
    if score_meta >= threshold:
        return metadata_index[match_meta]

    # fuzzy filename match
    match_file, score_file, _ = process.extractOne(ref, pdf_keys, scorer=fuzz.ratio)
    if score_file >= threshold:
        return pdf_filenames[match_file]

    return None

# Resolve references
for source_file, info in reference_map.items():
    resolved = {}

    # Normalize own case_id (from metadata)
    own_case_id = normalize_citation(file_case_index.get(source_file, ""))

    for ref in info["references"]:
        ref_norm = normalize_citation(ref)
        if not ref_norm:
            resolved[ref] = None
            continue

        # Skip self-citations
        if own_case_id and ref_norm == own_case_id:
            continue

        resolved[ref] = resolve_best_match(ref_norm)

    reference_map[source_file]["resolved"] = resolved

# Write output
with open(REFERENCE_FILE, "w") as f:
    json.dump(reference_map, f, indent=2)

print("✅ Resolved references (excluding self-citations).")
#we have to find every case number, then we have to identify which case number belogns to that particular file 
#another pattern to identify the case petitioner and respondent (person a vs person b) we need a pattern to identify that
#all the while this info shd be indexed, write a dictionary where all petit and respondents and all case number are indexed
#when we do this iteratively, and we find a reference to another case of the form ref to A vs B, go back to index where we had A had petitioner and B as respondent
#find potential reference using the index, 
#solve-> identify which case number belongs to that file
#for petitioner vs respondent (try ner)
#case_no, Petitioner, respondent-> indexes
#case number belonging to X file
#case number present in filename