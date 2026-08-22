from difflib import SequenceMatcher

from service.utils.text import sanitize_word

CLOSE_RATIO = 0.78


def score_text(word, text):
    """Return exact, close, or None for one string against the search word."""
    target = sanitize_word(word)
    candidate = sanitize_word(text)
    if not target or not candidate:
        return None
    if target == candidate:
        return "exact"
    ratio = SequenceMatcher(None, target, candidate).ratio()
    if target.startswith(candidate) or candidate.startswith(target):
        ratio = max(ratio, 0.85)
    if ratio >= CLOSE_RATIO:
        return "close"
    return None


def best_confidence(word, texts):
    best = None
    for text in texts:
        score = score_text(word, text)
        if score == "exact":
            return "exact"
        if score == "close":
            best = "close"
    return best


def form_has_audio(form):
    claims = form.get("claims") or {}
    return bool(claims.get("P443"))


def lemma_value(lexeme, lang_code):
    lemmas = lexeme.get("lemmas") or {}
    if lang_code and lang_code in lemmas:
        return lemmas[lang_code].get("value")
    if lemmas:
        return next(iter(lemmas.values())).get("value")
    return None


def form_representation(form, lang_code):
    reps = form.get("representations") or {}
    if lang_code and lang_code in reps:
        return reps[lang_code].get("value")
    if reps:
        return next(iter(reps.values())).get("value")
    return None


def representation_values(form):
    return [
        item.get("value")
        for item in (form.get("representations") or {}).values()
        if item.get("value")
    ]


def lemma_values(lexeme):
    return [
        item.get("value")
        for item in (lexeme.get("lemmas") or {}).values()
        if item.get("value")
    ]


def sort_candidates(candidates):
    def key(item):
        confidence_rank = 0 if item.get("confidence") == "exact" else 1
        audio_rank = 1 if item.get("already_has_audio") else 0
        return (confidence_rank, audio_rank, item.get("form_id") or "")

    return sorted(candidates, key=key)


def candidates_from_lexeme(lexeme, word, language_qid, lang_code):
    """Build ranked form candidates for one lexeme in one language."""
    if language_qid and lexeme.get("language") != language_qid:
        return []

    lemma = lemma_value(lexeme, lang_code)
    lemma_score = best_confidence(word, lemma_values(lexeme))
    candidates = []

    for form in lexeme.get("forms") or []:
        form_score = best_confidence(word, representation_values(form))
        if form_score:
            confidence = form_score
            matched_on = "form"
        elif lemma_score:
            confidence = lemma_score
            matched_on = "lemma"
        else:
            continue

        candidates.append({
            "lexeme_id": lexeme.get("id"),
            "form_id": form.get("id"),
            "lemma": lemma,
            "form_representation": form_representation(form, lang_code),
            "grammatical_features": form.get("grammaticalFeatures") or [],
            "confidence": confidence,
            "already_has_audio": form_has_audio(form),
            "matched_on": matched_on,
        })

    return sort_candidates(candidates)
