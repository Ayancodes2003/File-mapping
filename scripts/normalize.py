import re

def normalize_citation(citation: str) -> str:
    citation = citation.upper()
    citation = citation.replace("NO.", "")
    citation = citation.replace("/", "-")
    citation = citation.replace(" OF ", "-")
    citation = re.sub(r"[^A-Z0-9\-]", "-", citation)  # replace spaces and punctuation with -
    parts = re.findall(r"[A-Z]{2,5}|\d{1,5}|\d{4}", citation)
    return "-".join(parts) if parts else None
