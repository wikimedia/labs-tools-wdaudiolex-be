from common import commons_url
from service.resources.utils import make_api_request
from service.utils.ll_filename import file_title, parse_ll_filename


def _is_failed_request(payload):
    return bool(payload.get("error")) and bool(payload.get("status_code"))


def _transcription_value(claim):
    value = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
    if isinstance(value, dict):
        return value.get("text") or value.get("value")
    return value


def fetch_transcriptions(page_ids):
    if not page_ids:
        return {}
    media_ids = [f"M{page_id}" for page_id in page_ids]
    payload = make_api_request(
        commons_url,
        {
            "action": "wbgetentities",
            "ids": "|".join(media_ids),
            "props": "claims",
            "format": "json",
        },
    )
    if _is_failed_request(payload):
        return {}

    transcriptions = {}
    for media_id, entity in payload.get("entities", {}).items():
        page_id = media_id[1:] if media_id.startswith("M") else media_id
        claims = entity.get("claims", {}).get("P9533") or []
        if not claims:
            continue
        text = _transcription_value(claims[0])
        if text:
            transcriptions[str(page_id)] = text
    return transcriptions


def list_lingua_libre_files(iso3, continue_token=None, limit=50):
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": f"Category:Lingua Libre pronunciation-{iso3}",
        "gcmtype": "file",
        "gcmlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }
    if continue_token:
        params["gcmcontinue"] = continue_token

    payload = make_api_request(commons_url, params)
    if _is_failed_request(payload):
        return payload

    pages = payload.get("query", {}).get("pages", {})
    if not pages:
        return {"files": [], "continue": None}

    page_ids = [str(page.get("pageid")) for page in pages.values() if page.get("pageid")]
    transcriptions = fetch_transcriptions(page_ids)

    files = []
    for page in pages.values():
        parsed = parse_ll_filename(page.get("title", ""))
        imageinfo = page.get("imageinfo") or [{}]
        url = imageinfo[0].get("url")
        transcription = transcriptions.get(str(page.get("pageid")))
        word = parsed["word"] or transcription
        files.append({
            "title": parsed["title"] or page.get("title"),
            "url": url,
            "iso3": parsed["iso3"] or iso3,
            "lang_qid": parsed["lang_qid"],
            "speaker": parsed["speaker"],
            "word": word,
            "transcription": transcription,
        })

    continue_value = None
    cont = payload.get("continue") or {}
    continue_value = cont.get("gcmcontinue") or cont.get("continue")
    return {"files": files, "continue": continue_value}


def get_file_url(title):
    full_title = file_title(title)
    payload = make_api_request(
        commons_url,
        {
            "action": "query",
            "titles": full_title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        },
    )
    if _is_failed_request(payload):
        return payload

    pages = payload.get("query", {}).get("pages", {})
    if not pages:
        return {"title": full_title, "url": None}

    page = next(iter(pages.values()))
    if page.get("missing") is not None or "imageinfo" not in page:
        return {"title": page.get("title", full_title), "url": None}
    return {
        "title": page.get("title", full_title),
        "url": page["imageinfo"][0].get("url"),
    }
