import os
import json
import re
from extract_text import extract_text_from_pdf
from normalize import normalize_citation
from llm_resolver import extract_parties_ner

PDF_DIR = "data/raw_pdfs"
TEXT_DIR = "data/extracted_texts"
OUT_FILE = "data/case_index.json"

# --- Extract case number from text ---
def extract_case_number(text):
    match = re.search(
        r"(CWP|RSA|FAO|CRM|CR|CRA|CRR|LPA|RFA|CSA|C\.R\.|R\.S\.A\.|F\.A\.O\.)[\s\.\-]*No\.? a*([0-9]{1,5}[A-Z\-]*)\s*(of)?\s*(\d{4})",
        text,
        re.IGNORECASE
    )
    if match:
        case_type = match.group(1).replace(".", "").upper()
        return f"{case_type}-{match.group(2).strip()}-{match.group(4)}"
    return None

def extract_parties_regex(text):
    for line in text.split("\n")[:60]:
        match = re.search(r"(.+?)\s+(?:VS\.?|VERSUS|V\.?|v\.?|V\s)\s+(.+)", line, re.IGNORECASE)
        if match:
            petitioner = match.group(1).strip(" .")
            respondent = match.group(2).strip(" .")
            return petitioner, respondent
    return None, None

case_index = {}
for fname in os.listdir(PDF_DIR):
    if not fname.lower().endswith(".pdf"):
        continue
    pdf_path = os.path.join(PDF_DIR, fname)
    txt_path = os.path.join(TEXT_DIR, fname.replace(".pdf", ".txt"))

    if os.path.exists(txt_path):
        with open(txt_path, encoding="utf-8") as f:
            text = f.read()
    else:
        text = extract_text_from_pdf(pdf_path, max_pages=1)

    case_id = extract_case_number(text)
    if case_id:
        case_id = normalize_citation(case_id)

    petitioner, respondent = extract_parties_regex(text)
    if not petitioner or not respondent:
        petitioner, respondent = extract_parties_ner(text)

    if not case_id:
        case_id = normalize_citation(fname.replace(".pdf", ""))

    if case_id:
        case_index[case_id] = {
            "filename": fname,
            "petitioner": petitioner,
            "respondent": respondent
        }

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(case_index, f, indent=2, ensure_ascii=False)

print(f"✅ Indexed {len(case_index)} cases to {OUT_FILE}")