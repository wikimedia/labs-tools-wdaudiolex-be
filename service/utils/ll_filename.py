import re

from service.utils.text import sanitize_word

LL_RE = re.compile(
    r"^(?:File:)?LL-Q(\d+)\s*\(([^)]+)\)-(.+)\.([A-Za-z0-9]+)$",
    re.IGNORECASE,
)


def file_title(title):
    name = (title or "").strip()
    if not name:
        return ""
    if name.lower().startswith("file:"):
        return "File:" + name.split(":", 1)[1]
    return f"File:{name}"


def parse_ll_filename(title):
    """Parse a Lingua Libre Commons filename.

    Expected: LL-Q{qid} ({iso})-{speaker}-{word}.{ext}
    Speaker and word are split on the last hyphen so phrases stay intact.
    """
    raw = (title or "").strip()
    basename = raw[5:] if raw.lower().startswith("file:") else raw
    match = LL_RE.match(basename)
    if not match:
        return {
            "title": file_title(raw) if raw else "",
            "lang_qid": None,
            "iso3": None,
            "speaker": None,
            "word": None,
            "normalized_word": "",
            "extension": None,
        }

    remainder = match.group(3)
    if "-" in remainder:
        speaker, word = remainder.rsplit("-", 1)
    else:
        speaker, word = None, remainder

    return {
        "title": file_title(basename),
        "lang_qid": f"Q{match.group(1)}",
        "iso3": match.group(2).strip().lower(),
        "speaker": speaker,
        "word": word,
        "normalized_word": sanitize_word(word),
        "extension": match.group(4).lower(),
    }
