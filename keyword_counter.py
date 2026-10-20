from collections import Counter
import re

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "for", "from", "had", "has", "have", "he", "her", "his", "i", "in",
    "is", "it", "its", "me", "my", "of", "on", "or", "our", "she",
    "so", "that", "the", "their", "them", "there", "they", "this", "to",
    "was", "we", "were", "what", "when", "with", "you", "your"
}


def count_keywords(feedback_entries, top_n=10):
    """Return the most common meaningful words in feedback entries.

    feedback_entries may be strings or dictionaries containing a 'feedback'
    or 'customer_feedback' field. The result is a list of {word, count} dicts.
    """
    words = []
    for entry in feedback_entries:
        if isinstance(entry, dict):
            text = entry.get("feedback", entry.get("customer_feedback", ""))
        else:
            text = entry
        if not isinstance(text, str):
            continue
        for word in re.findall(r"[a-zA-Z]+", text.lower()):
            if word not in STOPWORDS and len(word) > 1:
                words.append(word)
    limit = max(0, int(top_n))
    return [{"word": word, "count": count} for word, count in Counter(words).most_common(limit)]
