import re


def sanitize_word(word):
    """Normalize a word or filename fragment for matching.

    Lowercases, strips whitespace, and removes punctuation while keeping
    letters and digits from any script (\\w).
    """
    if word is None:
        return ""
    return re.sub(r"[^\w\s]", "", str(word)).lower().strip()
