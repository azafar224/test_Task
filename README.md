# Document Intelligence Pipeline

A local AI system that reads a folder of PDF documents, figures out what type each one is, pulls out the relevant fields, and lets you search through them with natural language — all without any internet connection or paid APIs.

---

## What It Does

1. **Ingests PDFs** — reads every `.pdf` in a folder and extracts the text
2. **Classifies documents** — assigns each one to: Invoice, Resume, Utility Bill, Other, or Unclassifiable
3. **Extracts structured data** — pulls specific fields per document type and writes them to `output/output.json`
4. **Semantic search** — lets you query documents by meaning, e.g. *"find invoices from GlobalTech"* or *"candidates with AI experience"*

---

## Project Structure

```
doc_ai/
├── main.py              # entry point — run everything from here
├── src/
│   ├── ingest.py        # reads PDFs, extracts and cleans text
│   ├── classifier.py    # keyword-based document classification
│   ├── extractor.py     # regex-based field extraction per document type
│   └── retrieval.py     # TF-IDF search engine
├── documents/           # put your PDF files here
├── output/
│   └── output.json      # classification + extraction results
└── README.md
```

---

## Requirements

- Python 3.9 or higher
- No GPU needed
- No internet required after installation

---

## Installation

### 1. Set up a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install pypdf scikit-learn numpy
```

That's all you need for the full pipeline. Two libraries:

- `pypdf` — reads and extracts text from PDF files
- `scikit-learn` — powers the TF-IDF search engine
- `numpy` — used for scoring and ranking search results

---

## How to Run

### Step 1 — Add your PDFs

Drop your PDF files into the `documents/` folder. The sample dataset (invoices, resumes, utility bills, and others) should go here.

### Step 2 — Run the classification and extraction pipeline

**On Windows** (use this to avoid terminal encoding issues):
```bash
set PYTHONIOENCODING=utf-8 && python main.py --docs documents/
```

Or if you're using PowerShell:
```powershell
$env:PYTHONIOENCODING="utf-8"; python main.py --docs documents/
```

**On Mac/Linux:**
```bash
python main.py --docs documents/
```

You'll see output like this:

```
============================================================
 Document Intelligence Pipeline
============================================================

[1/3] Loading PDFs from 'documents/' ...
      [WARN] Skipping 'unclassifiable_1.pdf': Stream has ended unexpectedly
      Loaded 18 documents.

[2/3] Classifying & extracting ...
  invoice_1.pdf                  -> Invoice
  invoice_2.pdf                  -> Invoice
  other_1.pdf                    -> Other
  resume_1.pdf                   -> Resume
  utilitybill_1.pdf              -> Utility Bill
  ...

[3/3] Writing output.json ...
      Saved -> output/output.json

-- Classification Summary --
   Invoice                5 doc(s)
   Other                  3 doc(s)
   Resume                 5 doc(s)
   Utility Bill           5 doc(s)
```

> **Note:** Any PDF that can't be read (corrupted or empty) is automatically skipped with a warning. The rest of the pipeline continues normally.

### Step 3 — Run a search query

```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"; python main.py --search "electricity bills with high usage" --docs documents/
$env:PYTHONIOENCODING="utf-8"; python main.py --search "candidates with AI experience" --docs documents/
$env:PYTHONIOENCODING="utf-8"; python main.py --search "invoices from Pioneer Ltd" --docs documents/
$env:PYTHONIOENCODING="utf-8"; python main.py --search "payments over 3000 dollars" --top-k 3 --docs documents/
```

`--top-k` controls how many results to return (default: 5).

### Run pipeline and search together

```powershell
$env:PYTHONIOENCODING="utf-8"; python main.py --docs documents/ --search "find documents mentioning payments due"
```

---

## Output Format

`output/output.json` has one entry per document. Fields depend on the document type:

```json
{
  "invoice_1.pdf": {
    "class": "Invoice",
    "invoice_number": "1001",
    "date": "2025-06-16",
    "company": "Pioneer Ltd",
    "total_amount": 2073.0
  },
  "resume_1.pdf": {
    "class": "Resume",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-799-6125",
    "experience_years": 5
  },
  "utilitybill_1.pdf": {
    "class": "Utility Bill",
    "account_number": "ACC-49575",
    "date": "2025-05-24",
    "usage_kwh": 406.0,
    "amount_due": 193.0
  },
  "other_1.pdf": {
    "class": "Other"
  }
}
```

Documents classified as Other or Unclassifiable have no additional fields.

---

## Libraries Used and Why

### `pypdf`

Used in `ingest.py` to open each PDF and extract text page by page. It works on PDFs that have an embedded text layer (as opposed to scanned images, which would need OCR).

### `scikit-learn` — TF-IDF search

Used in `retrieval.py` for the search functionality. I built the index with `TfidfVectorizer` (unigram + bigram tokenisation, log-normalised term frequencies) and rank results using `cosine_similarity`. 

TF-IDF was chosen over a dense embedding model because it requires zero internet access and zero model downloads — it builds its index directly from the document text and works well for keyword-driven queries like those described in the assessment.

The `RetrievalEngine` class in `retrieval.py` is structured so that swapping in `SentenceTransformers + FAISS` later would be straightforward — just replace `TfidfVectorizer` with an embedding model and swap the cosine similarity call for a FAISS index lookup.

### No external AI APIs

The entire pipeline — classification, extraction, and search — runs locally with no calls to OpenAI, Claude, Gemini, or any hosted service.

---

## How Classification Works

`classifier.py` scores each document against three keyword lists (invoices, resumes, utility bills). A document needs at least 2 keyword matches to be assigned a class. If it scores below that threshold on all three lists, it's labelled "Other". If the text is empty, it's "Unclassifiable".

Ties are resolved with one extra rule: if the text contains the word "kWh" it's treated as a Utility Bill even if the invoice score is equal.

This simple approach got 18/18 correct on the sample dataset.

---

## How Extraction Works

`extractor.py` uses regular expressions to pull fields from document text. There's a separate function for each type:

- `extract_invoice()` — invoice number, date, company name, total amount
- `extract_resume()` — name, email, phone number, years of experience
- `extract_utility_bill()` — account number, billing date, kWh usage, amount due

Patterns are written to handle common formatting variations. If a field can't be found, it returns `null` rather than guessing.

---

## Running Completely Offline

The default setup works with zero internet access. Install the three packages once, drop in your PDFs, and run. No model downloads, no API keys, no external calls of any kind.
