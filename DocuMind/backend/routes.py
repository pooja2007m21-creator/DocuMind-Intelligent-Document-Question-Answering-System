from flask import Blueprint, jsonify, request
from . import database as db
from . import nlp_processor as nlp
from . import qa_engine as qa
from .document_loader import load, LoadError
from .utils import validate_doc, validate_question, word_count, error

api = Blueprint("api", __name__)

@api.get("/health")
def health(): return jsonify(status="ok")

@api.post("/documents")
def upload():
    if "file" in request.files and request.files["file"].filename:
        f = request.files["file"]; name = f.filename
        try: text = load(name, f.read())
        except LoadError as e: return error(str(e))
    else:
        d = request.get_json(silent=True)
        if not isinstance(d, dict) or not isinstance(d.get("text"), str):
            return error("Upload a file or paste some text.")
        text, name = d["text"], (d.get("name") or "Pasted text")
        if not isinstance(name, str): return error("Name must be text.")
    err = validate_doc(name, text)
    if err: return error(err)
    name = name.strip()[:150] or "Untitled"
    n_sent = len(nlp.sentences(nlp.clean_text(text)))
    if n_sent < 2: return error("The document needs at least two sentences.")
    i = db.add_doc(name, text.strip(), word_count(text), n_sent)
    return jsonify(id=i, name=name, word_count=word_count(text), sentence_count=n_sent, status="Document added successfully."), 201

@api.get("/documents")
def documents(): return jsonify(items=db.docs())

@api.get("/documents/<int:i>")
def document(i):
    r = db.get_doc(i)
    return jsonify(r) if r else error("Document not found.", 404)

@api.delete("/documents/<int:i>")
def document_del(i):
    qa.forget(i)
    return jsonify(deleted=True) if db.del_doc(i) else error("Document not found.", 404)

@api.post("/ask")
def ask():
    d = request.get_json(silent=True)
    if not isinstance(d, dict): return error("Invalid request.")
    err = validate_question(d.get("question"))
    if err: return error(err)
    try: doc = db.get_doc(int(d.get("document_id")))
    except (TypeError, ValueError): return error("Choose a document first.")
    if not doc: return error("Document not found.", 404)
    try: r = qa.answer(doc["id"], doc["content"], d["question"].strip())
    except Exception: return error("The question could not be processed. Please try again.", 500)
    db.add_q(doc["id"], d["question"].strip(), r["answer"], r["found"], r["strength"])
    return jsonify(**r, document=doc["name"])

@api.get("/history")
def history():
    try: doc = int(request.args.get("document_id")) if request.args.get("document_id") else None
    except ValueError: doc = None
    return jsonify(items=db.history(request.args.get("q", "").strip(), request.args.get("status", ""), doc))

@api.delete("/history/<int:i>")
def history_del(i): return jsonify(deleted=True) if db.del_q(i) else error("Not found.", 404)

@api.get("/stats")
def stats(): return jsonify(db.stats())
