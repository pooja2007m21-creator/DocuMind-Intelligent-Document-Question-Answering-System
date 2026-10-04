"""Preprocessing: cleaning, tokenization, stop-words, stemming."""
import re
import nltk
from nltk.stem import PorterStemmer

def _ensure(res, path):
    try: nltk.data.find(path)
    except LookupError:
        try: nltk.download(res, quiet=True)
        except Exception: pass
for r, p in [("punkt", "tokenizers/punkt"), ("punkt_tab", "tokenizers/punkt_tab"), ("stopwords", "corpora/stopwords")]:
    _ensure(r, p)
try:
    from nltk.corpus import stopwords
    STOP = set(stopwords.words("english"))
except Exception:
    STOP = set("a an the and or but if of to in on at by for with from as is are was were be been it its this that these those he she they we you i not no so than then there their his her our your will would can could should may might do does did have has had what who whom when where which why how".split())
# question words carry no topical meaning for retrieval
STOP |= {"what", "who", "when", "where", "which", "why", "how", "tell", "explain", "describe", "according"}
stemmer = PorterStemmer()

def clean_text(t):
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"-\n(?=\w)", "", t)          # re-join words hyphenated at line breaks (PDFs)
    t = re.sub(r"\s*\n\s*", " ", t)
    return re.sub(r"[ \t]+", " ", t).strip()

def sentences(t):
    try: s = nltk.sent_tokenize(t)
    except Exception: s = re.split(r"(?<=[.!?])\s+", t)
    return [x.strip() for x in s if len(x.strip()) > 1]

def words(t):
    try: return nltk.word_tokenize(t)
    except Exception: return re.findall(r"\w+|[^\w\s]", t)

def tokens(text):
    return [stemmer.stem(w.lower()) for w in words(text) if w.isalnum() and len(w) > 1 and w.lower() not in STOP]
