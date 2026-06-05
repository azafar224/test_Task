"""
classifier.py — Rule-based document classification.

Categories: Invoice | Resume | Utility Bill | Other | Unclassifiable
"""
import re

# ── keyword sets ──────────────────────────────────────────────────────────────
INVOICE_KEYWORDS = [
    "invoice", "inv-", "invoice #", "invoice number",
    "total amount", "bill to", "amount due", "payment terms",
    "subtotal", "tax", "purchase order",
]

RESUME_KEYWORDS = [
    "experience", "education", "skills", "resume", "curriculum vitae",
    "cv", "email:", "phone:", "summary:", "objective:",
    "work history", "employment",
]

UTILITY_KEYWORDS = [
    "utility", "kwh", "kilowatt", "electricity", "gas bill",
    "water bill", "billing date", "account number", "usage",
    "utility provider", "meter reading", "service address",
    "amount due", "cityelectric", "powergrid",
]


def _score(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for kw in keywords if kw in lower)


def classify(text: str) -> str:
    """Return the document category for the given text."""
    if not text.strip():
        return "Unclassifiable"

    inv   = _score(text, INVOICE_KEYWORDS)
    res   = _score(text, RESUME_KEYWORDS)
    util  = _score(text, UTILITY_KEYWORDS)

    best  = max(inv, res, util)

    # Require a minimum confidence threshold to assign a category
    # Documents that only weakly match keywords are "Other"
    MIN_SCORE = 2
    if best < MIN_SCORE:
        return "Other"

    # Resolve ties — utility bill wins if "kwh" present
    if util == best and re.search(r"\bkwh\b", text, re.IGNORECASE):
        return "Utility Bill"
    if inv == best:
        return "Invoice"
    if res == best:
        return "Resume"
    if util == best:
        return "Utility Bill"
    return "Other"
