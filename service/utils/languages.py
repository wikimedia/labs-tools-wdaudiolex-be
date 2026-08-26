import time

import requests
from langcodes import Language
from langcodes.tag_parser import LanguageTagError

from common import base_url, sparql_endpoint_url
from service.resources.utils import get_user_agent, make_api_request

CACHE_TTL_SECONDS = 6 * 60 * 60
_INDEX_CACHE = {}


class LanguageNotResolved(Exception):
    pass


def commons_category(iso3):
    if not iso3:
        return None
    return f"Lingua Libre pronunciation-{iso3}"


def language_record(iso=None, iso3=None, qid=None, label=None):
    return {
        "iso": iso,
        "iso3": iso3,
        "qid": qid,
        "label": label or iso3 or iso or qid,
        "commons_category": commons_category(iso3),
    }


def codes_from_tag(code):
    language = Language.get(code)
    iso = language.language
    iso3 = language.to_alpha3()
    iso1 = iso if iso and len(iso) == 2 else None
    return iso1, iso3


def display_label(code, ui_lang="en", fallback=None):
    try:
        return Language.get(code).display_name(ui_lang)
    except (LanguageTagError, ModuleNotFoundError, ValueError):
        return fallback or code


def from_iso3(iso3_code, ui_lang="en"):
    """Convert a Lingua Libre / Commons ISO 639-3 code for Wikidata.

    Commons categories use 639-3 (e.g. ibo). Wikidata lexeme search and
    lemma language keys usually want 639-1 (e.g. ig) when it exists.

    Returns iso (639-1 or None), iso3, English name, and localized label.
    Uses langcodes + language-data (same job as pyiso639, with i18n labels).
    """
    raw = (iso3_code or "").strip()
    if not raw:
        raise LanguageNotResolved("ISO 639-3 code is required")
    try:
        iso1, iso3 = codes_from_tag(raw)
    except (LanguageTagError, ValueError) as error:
        raise LanguageNotResolved(
            f"Unsupported ISO 639-3 code: {raw}"
        ) from error
    if not iso3:
        raise LanguageNotResolved(f"Could not derive ISO 639-3 from {raw}")
    name = display_label(iso1 or iso3, "en", fallback=iso3)
    label = display_label(iso1 or iso3, ui_lang, fallback=name)
    return {
        "iso": iso1,
        "iso3": iso3,
        "name": name,
        "label": label,
    }


def language_labels(iso3_code, ui_langs=None):
    """Return display labels for an ISO 639-3 code in one or more UI languages."""
    if ui_langs is None:
        ui_langs = ["en"]
    converted = from_iso3(iso3_code, "en")
    code = converted["iso"] or converted["iso3"]
    labels = {}
    for ui_lang in ui_langs:
        labels[ui_lang] = display_label(
            code, ui_lang, fallback=converted["name"]
        )
    return labels


def wikidata_lang_code(language):
    """Language tag Wikidata expects: ISO 639-1 when present, else 639-3."""
    iso = language.get("iso") if isinstance(language, dict) else None
    iso3 = language.get("iso3") if isinstance(language, dict) else None
    if iso:
        return iso
    if iso3:
        return from_iso3(iso3)["iso"] or iso3
    raise LanguageNotResolved("Language has no ISO 639-1 or 639-3 code")


def _cache_get(ui_lang):
    entry = _INDEX_CACHE.get(ui_lang)
    if not entry:
        return None
    if entry["expires"] < time.time():
        _INDEX_CACHE.pop(ui_lang, None)
        return None
    return entry["data"]


def _cache_set(ui_lang, data):
    _INDEX_CACHE[ui_lang] = {
        "expires": time.time() + CACHE_TTL_SECONDS,
        "data": data,
    }
    return data


def reset_language_cache():
    _INDEX_CACHE.clear()


def set_language_index_for_tests(ui_lang, data):
    _cache_set(ui_lang, data)


def _index_from_records(records):
    by_key = {}
    for record in records:
        for key in (record.get("iso"), record.get("iso3"), record.get("qid")):
            if key:
                by_key[str(key).lower()] = record
    return {"list": records, "by_key": by_key}


def _sparql_language_rows(ui_lang):
    query = f"""
    SELECT ?lang ?iso3 ?iso1 ?langLabel WHERE {{
      ?lang wdt:P220 ?iso3 .
      OPTIONAL {{ ?lang wdt:P218 ?iso1 . }}
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "{ui_lang},en".
      }}
    }}
    """
    response = requests.get(
        sparql_endpoint_url,
        params={"query": query, "format": "json"},
        headers=get_user_agent(),
        timeout=45,
    )
    response.raise_for_status()
    return response.json().get("results", {}).get("bindings", [])


def _index_from_sparql(ui_lang):
    records = []
    seen_qids = set()
    for row in _sparql_language_rows(ui_lang):
        qid = row["lang"]["value"].rsplit("/", 1)[-1]
        if qid in seen_qids:
            continue
        seen_qids.add(qid)
        iso3 = row.get("iso3", {}).get("value")
        iso1 = row.get("iso1", {}).get("value")
        label = row.get("langLabel", {}).get("value") or iso3 or qid
        records.append(language_record(iso1, iso3, qid, label))
    return _index_from_records(records)


def _index_from_commons(ui_lang):
    payload = make_api_request(
        "https://commons.wikimedia.org/w/api.php",
        {
            "action": "query",
            "meta": "languageinfo",
            "liprop": "code|name|autonym",
            "format": "json",
        },
    )
    if payload.get("error") and payload.get("status_code"):
        return _index_from_records([])

    records = []
    info = payload.get("query", {}).get("languageinfo", {})
    for code, meta in info.items():
        try:
            iso1, iso3 = codes_from_tag(code)
        except (LanguageTagError, ValueError):
            iso1, iso3 = (code if len(code) == 2 else None), (
                code if len(code) == 3 else None
            )
            if not iso3:
                continue
        label = display_label(
            iso1 or iso3,
            ui_lang,
            fallback=meta.get("name") or meta.get("autonym") or code,
        )
        records.append(language_record(iso1, iso3, None, label))
    return _index_from_records(records)


def get_language_index(ui_lang="en"):
    cached = _cache_get(ui_lang)
    if cached is not None:
        return cached
    try:
        data = _index_from_sparql(ui_lang)
        if data["list"]:
            return _cache_set(ui_lang, data)
    except Exception:
        pass
    return _cache_set(ui_lang, _index_from_commons(ui_lang))


def list_languages(ui_lang="en"):
    return get_language_index(ui_lang)["list"]


def _entity_claim_value(entity, prop):
    claims = entity.get("claims", {}).get(prop, [])
    if not claims:
        return None
    value = claims[0].get("mainsnak", {}).get("datavalue", {}).get("value")
    if isinstance(value, dict):
        return value.get("text") or value.get("id")
    return value


def _label_from_entity(entity, ui_lang):
    labels = entity.get("labels", {})
    if ui_lang in labels:
        return labels[ui_lang]["value"]
    if "en" in labels:
        return labels["en"]["value"]
    if labels:
        return next(iter(labels.values()))["value"]
    return None


def _resolve_qid_from_wikidata(qid, ui_lang):
    payload = make_api_request(
        base_url,
        {
            "action": "wbgetentities",
            "ids": qid,
            "props": "labels|claims",
            "languages": f"{ui_lang}|en",
            "format": "json",
        },
    )
    if payload.get("error") and payload.get("status_code"):
        raise LanguageNotResolved(f"Could not resolve language {qid}")
    entity = payload.get("entities", {}).get(qid)
    if not entity or entity.get("missing") is not None:
        raise LanguageNotResolved(f"Language {qid} was not found")
    iso3 = _entity_claim_value(entity, "P220")
    iso1 = _entity_claim_value(entity, "P218")
    if not iso3 and iso1:
        try:
            _, iso3 = codes_from_tag(iso1)
        except (LanguageTagError, ValueError):
            pass
    if not iso3:
        raise LanguageNotResolved(
            f"Language {qid} has no ISO 639-3 code (P220)"
        )
    label = _label_from_entity(entity, ui_lang) or display_label(
        iso1 or iso3, ui_lang, fallback=iso3
    )
    return language_record(iso1, iso3, qid, label)


def resolve_language(code, ui_lang="en"):
    raw = (code or "").strip()
    if not raw:
        raise LanguageNotResolved("Language code is required")

    index = get_language_index(ui_lang)
    by_key = index["by_key"]

    if raw[:1].upper() == "Q" and raw[1:].isdigit():
        qid = f"Q{raw[1:]}"
        found = by_key.get(qid.lower())
        if found and found.get("iso3"):
            return found
        return _resolve_qid_from_wikidata(qid, ui_lang)

    try:
        iso1, iso3 = codes_from_tag(raw)
    except (LanguageTagError, ValueError) as error:
        raise LanguageNotResolved(
            f"Unsupported language code: {raw}"
        ) from error

    for key in (iso3, iso1, raw.lower()):
        if key and key.lower() in by_key:
            found = by_key[key.lower()]
            if found.get("iso3"):
                return found

    record = language_record(
        iso1,
        iso3,
        None,
        display_label(iso1 or iso3, ui_lang, fallback=iso3),
    )
    if record["iso3"]:
        return record
    raise LanguageNotResolved(f"Could not resolve language {raw}")
