# DocuMind – Intelligent Document Question-Answering System

A full-stack NLP web app for the **Text and Speech Analysis** subject. Upload or paste a document, ask questions, and receive answers extracted only from that document, with the supporting passages shown.

> **Note:** Answers are produced by an automated NLP method and may be incomplete or wrong. Verify them against the source document before relying on them for academic or professional work.

## Problem statement
Finding specific facts in long documents is slow, and general chatbots may answer from outside knowledge instead of the document.

## Objective
Build a working system that answers questions using only the content of a user-provided document and shows its evidence.

## Features
Upload .txt/.pdf/.docx or paste text · multiple stored documents · question box with Enter-to-ask · answer with match strength · source passages with highlighted answer sentences · "not found" response when the document has no relevant content · history with search and answered/not-found filters · analytics dashboard (Chart.js) · dark/light mode · responsive layout · validation and friendly errors.

## Technology stack
HTML5, CSS3, vanilla JS · Python, Flask (REST) · NLTK, scikit-learn · pypdf, python-docx · SQLite · Chart.js (CDN).

## NLP workflow
Document → text extraction → cleaning → sentence tokenization → overlapping passages (3 sentences, stride 2) → tokenization, stop-word removal, stemming → TF-IDF index.
Question → same preprocessing → TF-IDF vector → cosine similarity to passages → top 3 passages → rank their sentences by similarity (plus a small bonus for dates/numbers on "when"/"how many" questions) → return the best 1–2 sentences in document order.
If similarity is below the thresholds (`MIN_PASSAGE=0.05`, `MIN_SENT=0.08` in `qa_engine.py`) the system answers that it could not find the answer. Match strength (Strong ≥ 0.35, Moderate ≥ 0.18, else Weak) is a heuristic, not an accuracy score.

## System architecture
Browser → Flask REST API (`routes.py`) → `document_loader.py` / `qa_engine.py` / `nlp_processor.py` → SQLite (`database.py`). Flask also serves the pages.

## Project structure
```text
DocuMind/
├── app.py  requirements.txt  README.md  .gitignore  (database.db is created on first run)
├── backend/   database.py routes.py qa_engine.py nlp_processor.py document_loader.py utils.py
├── frontend/  index/workspace/history/analytics/about .html, css/style.css, js/*.js
└── static/assets/
```

## Installation
```bash
python -m venv venv
venv\Scripts\activate        # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```
NLTK data downloads automatically on first run; offline, built-in fallbacks are used.

## How to run
```bash
python app.py
```
Open http://127.0.0.1:5000

## API documentation
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/documents` | multipart `file` (.txt/.pdf/.docx) or JSON `{"name","text"}` |
| GET | `/api/documents` | List documents |
| GET | `/api/documents/<id>` | One document with text |
| DELETE | `/api/documents/<id>` | Delete document and its questions |
| POST | `/api/ask` | `{"document_id","question"}` → `answer, found, strength, sources[]` |
| GET | `/api/history?q=&status=found\|notfound&document_id=` | Question history |
| DELETE | `/api/history/<id>` | Delete a history entry |
| GET | `/api/stats` | Totals, answer rate, questions over time |
| GET | `/api/health` | `{"status":"ok"}` |

Errors return `{"error": "<friendly message>"}`; stack traces stay in the server log.
Validation: unsupported or unreadable files, files over 5 MB, documents under 30 words or over 500,000 characters, empty or over-long questions, unknown document IDs.

## Database
`documents(id, name, content, word_count, sentence_count, created_at)` and `questions(id, document_id, question, answer, found, strength, created_at)`.

## Limitations
Extractive only: it returns existing sentences and does not reason or compute. Keyword-based, so paraphrased questions may miss. Scanned PDFs need OCR (not included). English-focused. No accuracy percentage is shown.

## Future enhancements
Semantic embeddings, transformer reader model, OCR, multi-document search, speech input, F1/exact-match evaluation.
