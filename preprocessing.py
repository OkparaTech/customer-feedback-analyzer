import re
import string


def clean_feedback(text):
    """Lowercase feedback and normalize punctuation and whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", text).strip()
