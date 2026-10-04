"""Extract plain text from .txt, .pdf and .docx uploads."""
import io, os
from .utils import ALLOWED

class LoadError(Exception): pass

def load(filename, data):
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in ALLOWED: raise LoadError("Unsupported file type. Upload a .txt, .pdf or .docx file.")
    try:
        if ext == ".txt":
            for enc in ("utf-8", "utf-16", "latin-1"):
                try: return data.decode(enc)
                except UnicodeDecodeError: continue
        if ext == ".pdf":
            from pypdf import PdfReader
            return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
        if ext == ".docx":
            from docx import Document
            return "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs)
    except ImportError:
        raise LoadError("Support for this file type is not installed. Run pip install -r requirements.txt.")
    except Exception:
        raise LoadError("The file could not be read. It may be damaged, scanned or password-protected.")
    raise LoadError("The file could not be decoded as text.")
