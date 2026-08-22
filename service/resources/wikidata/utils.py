from common import base_url
from service.resources.utils import make_api_request

SEARCH_LIMIT = 10


def _failed(payload):
    return bool(payload.get("error")) and bool(payload.get("status_code"))


def search_lexeme_ids(word, lang_code, limit=SEARCH_LIMIT):
    payload = make_api_request(
        base_url,
        {
            "action": "wbsearchentities",
            "format": "json",
            "language": lang_code,
            "uselang": lang_code,
            "type": "lexeme",
            "search": word,
            "limit": limit,
        },
    )
    if _failed(payload):
        return payload
    results = payload.get("search") or []
    return [item["id"] for item in results if item.get("id")]


def get_lexemes(lexeme_ids):
    if not lexeme_ids:
        return []
    payload = make_api_request(
        base_url,
        {
            "action": "wbgetentities",
            "ids": "|".join(lexeme_ids),
            "format": "json",
        },
    )
    if _failed(payload):
        return payload
    entities = payload.get("entities") or {}
    lexemes = []
    for lexeme_id in lexeme_ids:
        entity = entities.get(lexeme_id)
        if entity and entity.get("missing") is None:
            lexemes.append(entity)
    return lexemes
