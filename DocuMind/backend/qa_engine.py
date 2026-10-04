"""Retrieval-based extractive QA: passage TF-IDF retrieval -> sentence ranking -> answer from the document only."""
import re
from collections import OrderedDict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from . import nlp_processor as nlp

WIN, STRIDE, TOP_PASSAGES, MIN_PASSAGE, MIN_SENT = 3, 2, 3, 0.05, 0.08
_cache = OrderedDict()  # doc_id -> index (small LRU)
YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b|\b(january|february|march|april|may|june|july|august|september|october|november|december)\b", re.I)
NUM = re.compile(r"\d")

class Index:
    def __init__(self, text):
        self.sents = nlp.sentences(nlp.clean_text(text))
        n = len(self.sents)
        self.spans = [(i, min(n, i + WIN)) for i in range(0, max(1, n - WIN + STRIDE), STRIDE)]
        self.vec = TfidfVectorizer(analyzer=lambda x: x, sublinear_tf=True)
        self.M = self.vec.fit_transform([nlp.tokens(" ".join(self.sents[a:b])) for a, b in self.spans])

def get_index(doc_id, text):
    if doc_id not in _cache:
        _cache[doc_id] = Index(text)
        while len(_cache) > 8: _cache.popitem(last=False)
    _cache.move_to_end(doc_id)
    return _cache[doc_id]

def forget(doc_id): _cache.pop(doc_id, None)

def _bonus(q, s):
    ql = q.lower()
    if ql.startswith("when") or "what year" in ql: return 0.08 if YEAR.search(s) else 0
    if "how many" in ql or "how much" in ql: return 0.08 if NUM.search(s) else 0
    return 0

def answer(doc_id, text, question):
    ix = get_index(doc_id, text)
    qt = nlp.tokens(question)
    miss = {"answer": "I could not find an answer to that in this document.", "found": False, "strength": "None", "sources": []}
    if not qt: return {**miss, "answer": "Please ask a more specific question that uses key terms from the document."}
    qv = ix.vec.transform([qt])
    psim = cosine_similarity(qv, ix.M).ravel()
    top = [int(i) for i in np.argsort(-psim)[:TOP_PASSAGES] if psim[i] >= MIN_PASSAGE]
    if not top: return miss
    cand = sorted({i for p in top for i in range(*ix.spans[p])})
    sv = cosine_similarity(qv, ix.vec.transform([nlp.tokens(ix.sents[i]) for i in cand])).ravel()
    sc = {i: float(s) + _bonus(question, ix.sents[i]) * (s > 0) for i, s in zip(cand, sv)}
    best = max(sc.values())
    if best < MIN_SENT: return miss
    picked = sorted([i for i in sorted(sc, key=sc.get, reverse=True)[:2] if sc[i] >= 0.5 * best])
    strength = "Strong" if best >= 0.35 else "Moderate" if best >= 0.18 else "Weak"
    sources = [{"similarity": round(float(psim[p]), 3),
                "sentences": [{"text": ix.sents[i], "used": i in picked} for i in range(*ix.spans[p])]} for p in top]
    return {"answer": " ".join(ix.sents[i] for i in picked), "found": True, "strength": strength, "sources": sources}
