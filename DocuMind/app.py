"""DocuMind - Flask entry point. Run: python app.py"""
import os
from flask import Flask, send_from_directory, jsonify
from backend.database import init_db
from backend.routes import api

BASE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.join(BASE, "frontend")
app = Flask(__name__, static_folder=os.path.join(BASE, "static"), static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
app.register_blueprint(api, url_prefix="/api")
PAGES = {"": "index.html", "workspace": "workspace.html", "history": "history.html",
         "analytics": "analytics.html", "about": "about.html"}

@app.route("/", defaults={"page": ""})
@app.route("/<page>")
def page(page):
    if page in PAGES: return send_from_directory(FRONT, PAGES[page])
    return jsonify(error="Page not found."), 404

@app.route("/css/<path:f>")
def css(f): return send_from_directory(os.path.join(FRONT, "css"), f)

@app.route("/js/<path:f>")
def js(f): return send_from_directory(os.path.join(FRONT, "js"), f)

@app.errorhandler(413)
def too_big(_): return jsonify(error="The file is too large. Maximum size is 5 MB."), 413

@app.errorhandler(Exception)
def fail(e):
    if hasattr(e, "code") and isinstance(e.code, int) and e.code < 500:
        return jsonify(error="Invalid request."), e.code
    app.logger.exception(e)  # details stay in the server log
    return jsonify(error="Something went wrong. Please try again."), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="127.0.0.1", port=5000)
