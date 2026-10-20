from collections import Counter
from keyword_counter import count_keywords


def build_analytics(feedback_entries):
    """Build the JSON-ready analytics summary from stored feedback rows."""
    category_counts = Counter(
        (entry.get("category") or "Uncategorized") for entry in feedback_entries
    )
    return {
        "total_feedback": len(feedback_entries),
        "category_counts": dict(category_counts),
        "top_keywords": count_keywords(feedback_entries),
    }
