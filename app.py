import os
import sqlite3
import uuid

from flask import Flask, g, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "profiles.db")
UPLOADS = os.path.join(BASE, "static", "uploads")
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024
os.makedirs(UPLOADS, exist_ok=True)


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            about TEXT,
            image TEXT
        )"""
    )
    conn.commit()
    conn.close()


def save_image(file):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        return None
    name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(os.path.join(UPLOADS, name))
    return name


@app.route("/")
def index():
    rows = db().execute("SELECT * FROM profiles ORDER BY id DESC").fetchall()
    return render_template("index.html", profiles=rows)


@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        about = request.form.get("about", "").strip()
        if not name:
            return render_template("form.html", error="Name is required", profile=None)
        image = save_image(request.files.get("image"))
        conn = db()
        cur = conn.execute(
            "INSERT INTO profiles (name, about, image) VALUES (?, ?, ?)",
            (name, about, image),
        )
        conn.commit()
        return redirect(url_for("profile", pid=cur.lastrowid))
    return render_template("form.html", error=None, profile=None)


@app.route("/profile/<int:pid>")
def profile(pid):
    row = db().execute("SELECT * FROM profiles WHERE id = ?", (pid,)).fetchone()
    if row is None:
        return "Profile not found", 404
    return render_template("profile.html", p=row)


@app.route("/profile/<int:pid>/edit", methods=["GET", "POST"])
def edit(pid):
    conn = db()
    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (pid,)).fetchone()
    if row is None:
        return "Profile not found", 404
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        about = request.form.get("about", "").strip()
        if not name:
            return render_template("form.html", error="Name is required", profile=row)
        image = save_image(request.files.get("image")) or row["image"]
        conn.execute(
            "UPDATE profiles SET name = ?, about = ?, image = ? WHERE id = ?",
            (name, about, image, pid),
        )
        conn.commit()
        return redirect(url_for("profile", pid=pid))
    return render_template("form.html", error=None, profile=row)


@app.route("/profile/<int:pid>/delete", methods=["POST"])
def delete(pid):
    conn = db()
    row = conn.execute("SELECT image FROM profiles WHERE id = ?", (pid,)).fetchone()
    if row and row["image"]:
        path = os.path.join(UPLOADS, row["image"])
        if os.path.exists(path):
            os.remove(path)
    conn.execute("DELETE FROM profiles WHERE id = ?", (pid,))
    conn.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
