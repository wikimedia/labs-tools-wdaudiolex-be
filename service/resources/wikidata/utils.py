import json
import re

import requests

from common import base_url, consumer_key, consumer_secret
from service import db
from service.models import ContributionModel
from service.resources.utils import generate_csrf_token, get_user_agent, make_api_request
from service.utils.ll_filename import commons_media_name

SEARCH_LIMIT = 10
FORM_ID_RE = re.compile(r"^L\d+-F\d+$", re.IGNORECASE)
QID_RE = re.compile(r"^Q\d+$", re.IGNORECASE)


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


def _wikidata_error(payload):
    err = (payload or {}).get("error") or {}
    if not err:
        return None
    code = err.get("code", "error")
    info = err.get("info", "Wikidata request failed")
    return f"{code}: {info}"


def _normalize_qid(qid):
    raw = (qid or "").strip()
    if raw[:1].lower() == "q" and raw[1:].isdigit():
        return f"Q{raw[1:]}"
    return raw


def _set_item_qualifier(csrf_token, auth, claim_id, prop, qid):
    response = requests.post(
        base_url,
        data={
            "action": "wbsetqualifier",
            "claim": claim_id,
            "property": prop,
            "snaktype": "value",
            "value": json.dumps({"entity-type": "item", "id": qid}),
            "format": "json",
            "token": csrf_token,
        },
        auth=auth,
        headers=get_user_agent(),
        timeout=30,
    )
    payload = response.json()
    err = _wikidata_error(payload)
    if err:
        return {"error": err}
    return payload


def add_pronunciation_audio(
    username, auth_object, formid, filename, lang_wdqid, variety_qid=None
):
    """Write P443 on a lexeme form, then store a local contribution."""
    if not FORM_ID_RE.match(formid or ""):
        return {"error": "formid must look like L123-F1", "status_code": 400}
    lang_qid = _normalize_qid(lang_wdqid)
    if not QID_RE.match(lang_qid):
        return {"error": "lang_wdqid must look like Q33578", "status_code": 400}
    variety = _normalize_qid(variety_qid) if variety_qid else None
    if variety_qid and not QID_RE.match(variety or ""):
        return {"error": "variety_qid must look like Q123", "status_code": 400}

    media = commons_media_name(filename)
    if not media:
        return {"error": "filename is required", "status_code": 400}

    csrf = generate_csrf_token(
        base_url,
        consumer_key,
        consumer_secret,
        auth_object["access_token"],
        auth_object["access_secret"],
    )
    if isinstance(csrf, dict):
        return {
            "error": csrf.get("info", "Unable to get csrf token"),
            "status_code": csrf.get("status_code", 503),
        }
    csrf_token, api_auth = csrf

    try:
        claim_response = requests.post(
            base_url,
            data={
                "action": "wbcreateclaim",
                "entity": formid,
                "property": "P443",
                "snaktype": "value",
                "value": json.dumps(media),
                "format": "json",
                "token": csrf_token,
            },
            auth=api_auth,
            headers=get_user_agent(),
            timeout=30,
        )
        claim_payload = claim_response.json()
    except Exception as error:
        return {"error": f"Wikidata claim failed: {error}", "status_code": 503}

    err = _wikidata_error(claim_payload)
    if err:
        return {"error": err, "status_code": 503}

    claim = claim_payload.get("claim") or {}
    claim_id = claim.get("id")
    revision_id = str(
        (claim_payload.get("pageinfo") or {}).get("lastrevid") or ""
    )
    warnings = []
    if claim_id:
        p407 = _set_item_qualifier(
            csrf_token, api_auth, claim_id, "P407", lang_qid
        )
        if p407.get("error"):
            warnings.append(f"P407: {p407['error']}")
        else:
            revision_id = str(
                (p407.get("pageinfo") or {}).get("lastrevid") or revision_id
            )
        if variety:
            p5237 = _set_item_qualifier(
                csrf_token, api_auth, claim_id, "P5237", variety
            )
            if p5237.get("error"):
                warnings.append(f"P5237: {p5237['error']}")
            else:
                revision_id = str(
                    (p5237.get("pageinfo") or {}).
                    get("lastrevid") or revision_id
                )

    lexeme_id = formid.split("-")[0]
    contribution = ContributionModel(
        wd_item=lexeme_id,
        form_id=formid,
        username=username,
        lang_code=lang_qid,
        audio_filename=media,
        variety_qid=variety,
        edit_type="pronunciation_audio",
        data=f"{formid}-{media}",
        revision_id=revision_id or None,
    )
    db.session.add(contribution)
    db.session.commit()

    return {
        "lexeme_id": lexeme_id,
        "form_id": formid,
        "revision_id": revision_id or None,
        "contribution_id": contribution.id,
        "filename": media,
        "warnings": warnings,
    }
