import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from analytics_api import build_analytics

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "feedback.db"
app = Flask(__name__)


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_feedback TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def fetch_feedback():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, customer_feedback, category, created_at FROM feedback ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/feedback")
def add_feedback():
    data = request.get_json(silent=True) or request.form
    text = data.get("customer_feedback", data.get("feedback", ""))
    category = data.get("category", "General")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Feedback text is required."}), 400
    if not isinstance(category, str) or not category.strip():
        category = "General"
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO feedback (customer_feedback, category) VALUES (?, ?)",
            (text.strip(), category.strip())
        )
        feedback_id = cursor.lastrowid
    return jsonify({"message": "Feedback saved.", "id": feedback_id}), 201


@app.get("/feedback")
def list_feedback():
    return jsonify(fetch_feedback())


@app.get("/analytics")
def analytics():
    return jsonify(build_analytics(fetch_feedback()))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
