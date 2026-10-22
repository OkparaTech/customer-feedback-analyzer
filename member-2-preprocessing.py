import re
import string


def clean_feedback(text):
    """Lowercase feedback and normalize punctuation and whitespace."""
    if not isinstance(text, str):
        return "This is not a feedback"
    text = text.lower()
    text = re.sub(r"[^\w\s₦$€£¥₹]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


feedback = " 1 The FOOD!!!   is   GOOD AT $5  "
print(clean_feedback(feedback))

