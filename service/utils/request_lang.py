def get_ui_lang(request, default="en"):
    """Pick a UI language from ui_lang, then Accept-Language, then default."""
    query_lang = (request.args.get("ui_lang") or "").strip()
    if query_lang:
        return query_lang.split("-")[0]

    header = request.headers.get("Accept-Language") or ""
    if header:
        first = header.split(",")[0].split(";")[0].strip()
        if first:
            return first.split("-")[0]
    return default
