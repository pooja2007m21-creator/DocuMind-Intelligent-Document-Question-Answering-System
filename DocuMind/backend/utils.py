import re
from flask import jsonify
MIN_WORDS, MAX_CHARS, MAX_Q = 30, 500_000, 500
ALLOWED = {".txt", ".pdf", ".docx"}

def word_count(t): return len(re.findall(r"\b[\w'-]+\b", t or ""))
def error(msg, code=400): return jsonify(error=msg), code

def validate_doc(name, text):
    if not text or not text.strip(): return "The document has no readable text."
    if len(text) > MAX_CHARS: return f"The document is too long. Keep it under {MAX_CHARS:,} characters."
    if word_count(text) < MIN_WORDS: return f"The document is too short. Provide at least {MIN_WORDS} words."
    return None

def validate_question(q):
    if not isinstance(q, str) or not q.strip(): return "Please type a question."
    if len(q.strip()) < 3: return "The question is too short."
    if len(q) > MAX_Q: return f"Keep the question under {MAX_Q} characters."
    return None
