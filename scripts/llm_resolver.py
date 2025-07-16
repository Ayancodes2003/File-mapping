import os
from dotenv import load_dotenv
import spacy
from sentence_transformers import SentenceTransformer, util

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Load spaCy NER
spacy_nlp = spacy.load("en_core_web_sm")

# Load MiniLM model
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_parties_ner(text):
    doc = spacy_nlp(text[:2000])
    parties = [ent.text for ent in doc.ents if ent.label_ in ("ORG", "PERSON")]
    if len(parties) >= 2:
        return parties[0], parties[1]
    return None, None

def resolve_with_semantic_match(party_line, case_index):
    # Build candidate list
    candidates = []
    case_ids = []
    for cid, entry in case_index.items():
        if entry.get('petitioner') and entry.get('respondent'):
            candidates.append(f"{entry['petitioner']} vs {entry['respondent']}")
            case_ids.append(cid)
    if not candidates:
        return None
    # Encode
    party_emb = model.encode([party_line], convert_to_tensor=True)
    cand_embs = model.encode(candidates, convert_to_tensor=True)
    # Compute similarity
    scores = util.pytorch_cos_sim(party_emb, cand_embs)[0]
    best_idx = int(scores.argmax())
    if float(scores[best_idx]) > 0.75:
        return case_ids[best_idx]
    return None
