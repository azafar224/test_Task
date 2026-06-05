"""
ingest.py — PDF text extraction and cleaning
"""
import re
from pathlib import Path
from pypdf import PdfReader


def extract_text(pdf_path: str) -> str:
    """Extract and clean text from a PDF file."""
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    raw = "\n".join(pages)
    # Normalise whitespace
    cleaned = re.sub(r"[ \t]+", " ", raw)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def load_documents(folder: str) -> dict[str, str]:
    """Load all PDFs from *folder* and return {filename: text}."""
    docs: dict[str, str] = {}
    for path in sorted(Path(folder).glob("*.pdf")):
        try:
            text = extract_text(str(path))
            docs[path.name] = text
        except Exception as e:
            print(f"      [WARN] Skipping '{path.name}': {e}")
    return docs
