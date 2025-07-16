import os
import fitz
from tqdm import tqdm

INPUT_DIR = "data/raw_pdfs"
OUTPUT_DIR = "data/extracted_texts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Reusable function
def extract_text_from_pdf(file_path, max_pages=None):
    doc = fitz.open(file_path)
    text = ""
    for i, page in enumerate(doc):
        if max_pages is not None and i >= max_pages:
            break
        text += page.get_text()
    return text

# ✅ Main script for full extraction
if __name__ == "__main__":
    for file in tqdm(os.listdir(INPUT_DIR)):
        if file.lower().endswith(".pdf"):
            input_path = os.path.join(INPUT_DIR, file)
            text = extract_text_from_pdf(input_path)
            out_path = os.path.join(OUTPUT_DIR, file.replace(".pdf", ".txt"))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
