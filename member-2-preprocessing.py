import re
import string


def clean_feedback(text):
    """Lowercase feedback and normalize punctuation and whitespace."""
    if not isinstance(text, str):
        return "This is not a feedback"
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


feedback = "  The FOOD!!!   is   GOOD @#$  "
print(clean_feedback(feedback))

