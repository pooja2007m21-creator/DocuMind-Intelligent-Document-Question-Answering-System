import os, sqlite3
DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database.db")

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, content TEXT NOT NULL,
            word_count INTEGER NOT NULL, sentence_count INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')));
        CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY AUTOINCREMENT, document_id INTEGER NOT NULL,
            question TEXT NOT NULL, answer TEXT NOT NULL, found INTEGER NOT NULL, strength TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')));""")

def _q(sql, args=(), one=False, write=False):
    init_db()
    with conn() as c:
        cur = c.execute(sql, args)
        if write: return cur.lastrowid if sql.startswith("INSERT") else cur.rowcount
        rows = [dict(r) for r in cur.fetchall()]
        return (rows[0] if rows else None) if one else rows

def add_doc(name, text, wc, sc):
    return _q("INSERT INTO documents(name,content,word_count,sentence_count) VALUES(?,?,?,?)", (name, text, wc, sc), write=True)
def docs(): return _q("SELECT id,name,word_count,sentence_count,created_at FROM documents ORDER BY id DESC")
def get_doc(i): return _q("SELECT * FROM documents WHERE id=?", (i,), one=True)
def del_doc(i):
    _q("DELETE FROM questions WHERE document_id=?", (i,), write=True)
    return _q("DELETE FROM documents WHERE id=?", (i,), write=True) > 0

def add_q(doc_id, q, a, found, strength):
    return _q("INSERT INTO questions(document_id,question,answer,found,strength) VALUES(?,?,?,?,?)", (doc_id, q, a, int(found), strength), write=True)
def history(q="", status="", doc_id=None):
    sql, a = "SELECT q.*, d.name document FROM questions q JOIN documents d ON d.id=q.document_id WHERE 1=1", []
    if q: sql += " AND (q.question LIKE ? OR q.answer LIKE ?)"; a += [f"%{q}%"] * 2
    if status in ("found", "notfound"): sql += " AND q.found=?"; a.append(1 if status == "found" else 0)
    if doc_id: sql += " AND q.document_id=?"; a.append(doc_id)
    return _q(sql + " ORDER BY q.id DESC", a)
def del_q(i): return _q("DELETE FROM questions WHERE id=?", (i,), write=True) > 0

def stats():
    d = _q("SELECT COUNT(*) n, COALESCE(SUM(word_count),0) w, COALESCE(AVG(word_count),0) a FROM documents", one=True)
    q = _q("SELECT COUNT(*) n, COALESCE(SUM(found),0) f FROM questions", one=True)
    over = _q("SELECT date(created_at) d, COUNT(*) n FROM questions GROUP BY d ORDER BY d")
    return {"total_documents": d["n"], "total_words": d["w"], "avg_document_words": round(d["a"], 1),
            "total_questions": q["n"], "answered": q["f"], "not_found": q["n"] - q["f"],
            "answer_rate": round(100 * q["f"] / q["n"], 1) if q["n"] else 0,
            "over_time": [{"date": r["d"], "count": r["n"]} for r in over]}
