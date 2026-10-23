"""Customer Feedback Analyzer - complete backend in one file.

Sections (each can be moved to its own file later):
  1. Setup & database                  (Member 1)
  2. clean_feedback                    (Member 2 - preprocessing.py)
  3. count_keywords                    (Member 3 - keyword_counter.py)
  4. categorize_feedback + analytics   (Member 4 - analytics_api.py)
  5. Routes: /, POST|GET /feedback, GET /analytics
"""
import re
import sqlite3
from collections import Counter
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request
from jinja2 import TemplateNotFound

# =====================================================================
# 1. SETUP & DATABASE  (Member 1)
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "feedback.db"
MAX_LENGTH = 1000

app = Flask(__name__)


def get_db():
    """One database connection per request (closed automatically)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_feedback TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'General',
                sentiment TEXT NOT NULL DEFAULT 'Neutral',
                created_at TEXT NOT NULL
            )
            """
        )
        columns = [r[1] for r in conn.execute("PRAGMA table_info(feedback)")]
        if "sentiment" not in columns:  # upgrade an older database
            conn.execute("ALTER TABLE feedback ADD COLUMN sentiment TEXT NOT NULL DEFAULT 'Neutral'")
            for row_id, text in conn.execute("SELECT id, customer_feedback FROM feedback").fetchall():
                conn.execute("UPDATE feedback SET sentiment = ? WHERE id = ?",
                             (analyze_sentiment(text), row_id))
        conn.commit()


def fetch_all_feedback():
    rows = get_db().execute(
        "SELECT id, customer_feedback, category, sentiment, created_at "
        "FROM feedback ORDER BY id DESC"
    ).fetchall()
    return [dict(row) for row in rows]


# =====================================================================
# 2. TEXT PREPROCESSING  (Member 2)
# =====================================================================
allowed_punct = [",", ".", "-", "'", "*", "$", "&", "#", "!"]


def clean_feedback(text):
    """Lowercase, remove unwanted punctuation/special characters, fix extra spaces."""
    if not isinstance(text, str):
        return ""

    text = text.lower()

    # Keep letters, numbers, spaces, and the allowed punctuation
    allowed = re.escape("".join(allowed_punct))
    text = re.sub(rf"[^\w\s{allowed}]", " ", text)

    # Remove underscores because \w includes them
    text = re.sub(r"_", " ", text)

    # Collapse extra spaces
    return re.sub(r"\s+", " ", text).strip()


# =====================================================================
# 3. KEYWORD FREQUENCY COUNTER  (Member 3)
# =====================================================================
STOPWORDS = {
    "a", "about", "all", "also", "am", "an", "and", "any", "are", "as", "at",
    "be", "been", "but", "by", "can", "did", "do", "does", "for", "from",
    "had", "has", "have", "he", "her", "his", "how", "i", "if", "im", "in",
    "is", "it", "its", "just", "me", "more", "most", "my", "no", "not", "of",
    "on", "or", "our", "she", "so", "some", "than", "that", "the", "their",
    "them", "then", "there", "these", "they", "this", "those", "to", "too",
    "very", "was", "we", "were", "what", "when", "which", "who", "will",
    "with", "would", "you", "your",
}


def count_keywords(feedback_entries, top_n=10):
    """Return the top_n most frequent meaningful words.

    feedback_entries: list of strings, or list of dicts containing
    'customer_feedback'. Returns [{"word": ..., "count": ...}, ...].
    """
    words = []
    for entry in feedback_entries:
        text = entry.get("customer_feedback", "") if isinstance(entry, dict) else entry
        for word in re.findall(r"[a-z0-9']+", clean_feedback(text)):
            word = word.strip("'")
            if word not in STOPWORDS and len(word) > 1 and not word.isdigit():
                words.append(word)
    return [
        {"word": word, "count": count}
        for word, count in Counter(words).most_common(max(0, int(top_n)))
    ]


# =====================================================================
# 4. CATEGORIZATION & ANALYTICS  (Member 4)
# =====================================================================
SENTIMENTS = ["Positive", "Neutral", "Negative"]
TOPICS = ["General", "Delivery", "Product", "Customer Service", "Pricing", "Feature Request"]

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "love", "loved", "happy",
    "fast", "friendly", "helpful", "easy", "perfect", "fantastic", "wonderful",
    "best", "nice", "satisfied", "smooth", "quick", "recommend", "impressed",
    "pleased", "enjoy", "enjoyed", "reliable", "thanks", "thank", "brilliant",
    "superb", "outstanding", "convenient", "affordable", "comfortable",
    "responsive", "intuitive", "clean", "beautiful",
}
NEGATIVE_WORDS = {
    "bad", "terrible", "poor", "worst", "awful", "slow", "late", "broken",
    "disappointed", "disappointing", "rude", "unhelpful", "bug", "bugs",
    "crash", "crashes", "crashed", "error", "errors", "fail", "failed",
    "useless", "horrible", "delay", "delayed", "damaged", "wrong", "missing",
    "refund", "complaint", "problem", "problems", "issue", "issues",
    "difficult", "confusing", "frustrating", "annoying", "hate", "waste",
    "expensive", "overpriced", "pricey",
}
NEGATIVE_PHRASES = ("too high", "too expensive", "too slow", "not working",
                    "doesn't work", "does not work", "didn't work", "are not")
NEGATORS = {"not", "no", "never", "dont", "don't", "isn't", "wasn't",
            "cant", "can't", "hardly", "wont", "won't", "didn't"}
FEATURE_WORDS = {"add", "wish", "feature", "features", "suggest", "suggestion",
                 "request", "should", "need", "needs", "could"}
FEATURE_PHRASES = ("would be nice", "would love", "would be great",
                   "please add", "i wish", "it would be")

# Words that show which topic a message is really about
TOPIC_KEYWORDS = {
    "Delivery": {"delivery", "delivered", "deliver", "shipping", "shipped", "shipment",
                 "courier", "dispatch", "arrived", "arrive", "package", "parcel",
                 "tracking", "rider", "driver", "late"},
    "Pricing": {"price", "prices", "pricing", "cost", "costs", "expensive", "cheap",
                "cheaper", "overpriced", "pricey", "discount", "fee", "fees",
                "charge", "charged", "worth", "money", "billing", "bill", "paid"},
    "Product": {"product", "products", "quality", "item", "items", "size", "color",
                "colour", "defective", "material", "durable", "goods", "battery", "screen"},
    "Customer Service": {"service", "support", "staff", "agent", "representative",
                         "rude", "unhelpful", "response", "responded", "reply", "replied", "care"},
}


def is_feature_request(text):
    lowered = text.lower()
    tokens = re.findall(r"[a-z']+", lowered)
    return any(p in lowered for p in FEATURE_PHRASES) or any(t in FEATURE_WORDS for t in tokens)


def detect_topic(text, chosen="General"):
    """Keep the user's topic unless the text clearly belongs to a different one."""
    if chosen == "Feature Request":
        return chosen
    lowered = text.lower()
    tokens = re.findall(r"[a-z']+", lowered)
    scores = {t: sum(1 for w in tokens if w in words) for t, words in TOPIC_KEYWORDS.items()}
    if "$" in lowered or "₦" in lowered:
        scores["Pricing"] += 1
    top = max(scores.values())
    if top == 0:
        return chosen
    best = [t for t, n in scores.items() if n == top]
    if chosen in best or len(best) != 1:
        return chosen                      # already right, or too unclear to change
    return best[0]


def analyze_sentiment(text):
    """Rule-based sentiment: Positive, Neutral or Negative."""
    lowered = text.lower()
    tokens = re.findall(r"[a-z']+", lowered)
    positive = 0
    negative = sum(1 for p in NEGATIVE_PHRASES if p in lowered)
    for i, token in enumerate(tokens):
        negated = i > 0 and tokens[i - 1] in NEGATORS
        if token in POSITIVE_WORDS:
            if negated:
                negative += 1
            else:
                positive += 1
        elif token in NEGATIVE_WORDS:
            if negated:
                positive += 1
            else:
                negative += 1

    if positive > negative:
        return "Positive"
    if negative > positive:
        return "Negative"
    return "Neutral"


def _entry_date(entry):
    try:
        return datetime.fromisoformat(entry["created_at"]).date()
    except (KeyError, TypeError, ValueError):
        return None


def build_analytics(entries, top_n=10):
    total = len(entries)

    def pct(n):
        return round(100 * n / total, 1) if total else 0.0

    sent = Counter(e.get("sentiment", "Neutral") for e in entries)
    sentiment_counts = {s: sent.get(s, 0) for s in SENTIMENTS}
    sentiment_percentages = {s: pct(n) for s, n in sentiment_counts.items()}
    cats = Counter(e["category"] for e in entries)
    category_counts = {c: cats.get(c, 0) for c in TOPICS}
    for extra, n in cats.items():            # keep any unexpected category
        category_counts.setdefault(extra, n)
    category_percentages = {c: pct(n) for c, n in category_counts.items()}

    today = datetime.now(timezone.utc).date()
    per_day = Counter(d for d in map(_entry_date, entries) if d)
    daily_counts = [
        {"date": (today - timedelta(days=i)).isoformat(),
         "count": per_day.get(today - timedelta(days=i), 0)}
        for i in range(6, -1, -1)
    ]
    last_7 = sum(d["count"] for d in daily_counts)
    previous_7 = sum(per_day.get(today - timedelta(days=i), 0) for i in range(7, 14))
    change = round(100 * (last_7 - previous_7) / previous_7, 1) if previous_7 else None

    return {
        "total_feedback": total,
        "sentiment_counts": sentiment_counts,
        "sentiment_percentages": sentiment_percentages,
        "category_counts": category_counts,
        "category_percentages": category_percentages,
        "top_keywords": count_keywords(entries, top_n),
        "recent_activity": {
            "last_7_days": last_7,
            "previous_7_days": previous_7,
            "change_percent": change,
            "daily_counts": daily_counts,
        },
    }


# =====================================================================
# 5. ROUTES
# =====================================================================
@app.route("/")
def index():
    try:
        return render_template("index.html")
    except TemplateNotFound:
        return (
            "<h1>Customer Feedback Analyzer</h1>"
            "<p>The API is running. Try <a href='/feedback'>/feedback</a> or "
            "<a href='/analytics'>/analytics</a>. Add templates/index.html "
            "to show the dashboard.</p>"
        )


@app.route("/feedback", methods=["POST"])
def save_feedback():
    data = request.get_json(silent=True)
    if data is None:
        data = request.form
    if not hasattr(data, "get"):
        return jsonify(error="Request body must be an object"), 400

    text = data.get("customer_feedback")
    if text is None:
        return jsonify(error="customer_feedback is required"), 400
    if not isinstance(text, str):
        return jsonify(error="customer_feedback must be a string"), 400

    text = text.strip()
    if not text:
        return jsonify(error="customer_feedback cannot be empty"), 400
    if len(text) > MAX_LENGTH:
        return jsonify(error=f"customer_feedback must be {MAX_LENGTH} characters or fewer"), 400

    category = data.get("category")
    if category not in TOPICS:
        category = "General"
    category = detect_topic(text, category)
    if category == "General" and is_feature_request(text):
        category = "Feature Request"
    sentiment = analyze_sentiment(text)
    text = clean_feedback(text)
    if not text:
        return jsonify(error="customer_feedback cannot be empty"), 400

    created_at = datetime.now(timezone.utc).isoformat()

    db = get_db()
    cursor = db.execute(
        "INSERT INTO feedback (customer_feedback, category, sentiment, created_at) VALUES (?, ?, ?, ?)",
        (text, category, sentiment, created_at),
    )
    db.commit()

    return jsonify(
        id=cursor.lastrowid,
        customer_feedback=text,
        category=category,
        sentiment=sentiment,
        created_at=created_at,
    ), 201


@app.route("/feedback", methods=["GET"])
def get_feedback():
    return jsonify(fetch_all_feedback())


@app.route("/analytics", methods=["GET"])
def get_analytics():
    try:
        top_n = int(request.args.get("top_n", 10))
    except ValueError:
        top_n = 10
    return jsonify(build_analytics(fetch_all_feedback(), top_n))


init_db()

if __name__ == "__main__":
    app.run(debug=True)