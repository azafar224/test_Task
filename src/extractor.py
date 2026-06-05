"""
extractor.py — Regex-based structured data extraction.

Supported types: Invoice, Resume, Utility Bill
"""
import re
from typing import Any


# ── helpers ───────────────────────────────────────────────────────────────────

def _first(pattern: str, text: str, flags: int = re.IGNORECASE) -> str | None:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def _float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = re.sub(r"[,$]", "", value)
    try:
        return float(cleaned)
    except ValueError:
        return None


def _int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    m = re.search(r"\d+", value)
    return int(m.group()) if m else None


# ── per-type extractors ───────────────────────────────────────────────────────

def extract_invoice(text: str) -> dict[str, Any]:
    invoice_number = (
        _first(r"Invoice\s*#\s*(\S+)", text)
        or _first(r"Invoice\s+Number[:\s]+(\S+)", text)
        or _first(r"INV[-\s](\S+)", text)
    )
    date = (
        _first(r"Date[:\s]+(\d{4}-\d{2}-\d{2})", text)
        or _first(r"Date[:\s]+([\w\s,]+\d{4})", text)
    )
    company = (
        _first(r"Company[:\s]+(.+)", text)
        or _first(r"Bill(?:ed)? To[:\s]+(.+)", text)
        or _first(r"From[:\s]+(.+)", text)
    )
    total_amount = _float_or_none(
        _first(r"Total\s+Amount[:\s]+\$?([\d,]+\.?\d*)", text)
        or _first(r"Total[:\s]+\$?([\d,]+\.?\d*)", text)
        or _first(r"Amount\s+Due[:\s]+\$?([\d,]+\.?\d*)", text)
    )
    return {
        "invoice_number": invoice_number,
        "date": date,
        "company": company,
        "total_amount": total_amount,
    }


def extract_resume(text: str) -> dict[str, Any]:
    # Name — first non-empty line that doesn't look like a header keyword
    name = None
    for line in text.splitlines():
        line = line.strip()
        if line and not re.match(
            r"(resume|cv|curriculum|summary|objective|experience|education|skills)",
            line, re.IGNORECASE
        ):
            name = line
            break

    email = _first(r"([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})", text)
    phone = _first(
        r"(?:Phone|Tel|Mobile)[:\s]*([\+\d\s\-().]{7,20})", text
    ) or _first(r"(\+?1[\s\-]?\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4})", text)

    exp_years = _int_or_none(
        _first(r"(\d+)\s+years?(?:\s+of)?\s+experience", text)
        or _first(r"Experience[:\s]+(\d+)\s+years?", text)
    )

    return {
        "name": name,
        "email": email,
        "phone": phone.strip() if phone else None,
        "experience_years": exp_years,
    }


def extract_utility_bill(text: str) -> dict[str, Any]:
    account_number = (
        _first(r"Account\s+Number[:\s]+([\w\-]+)", text)
        or _first(r"Acc(?:ount)?[#\-:\s]+([\w\-]+)", text)
    )
    date = (
        _first(r"Billing\s+Date[:\s]+(\d{4}-\d{2}-\d{2})", text)
        or _first(r"(?:Bill|Due)\s+Date[:\s]+([\w\s,]+\d{4})", text)
    )
    usage_kwh = _float_or_none(
        _first(r"Usage[:\s]+([\d,]+\.?\d*)\s*kWh", text)
        or _first(r"([\d,]+\.?\d*)\s*kWh", text)
    )
    amount_due = _float_or_none(
        _first(r"Amount\s+Due[:\s]+\$?([\d,]+\.?\d*)", text)
        or _first(r"Total\s+Due[:\s]+\$?([\d,]+\.?\d*)", text)
    )
    return {
        "account_number": account_number,
        "date": date,
        "usage_kwh": usage_kwh,
        "amount_due": amount_due,
    }


# ── dispatch ──────────────────────────────────────────────────────────────────

def extract(doc_class: str, text: str) -> dict[str, Any]:
    """Return extracted fields for the given classification, or {} if N/A."""
    if doc_class == "Invoice":
        return extract_invoice(text)
    if doc_class == "Resume":
        return extract_resume(text)
    if doc_class == "Utility Bill":
        return extract_utility_bill(text)
    return {}
