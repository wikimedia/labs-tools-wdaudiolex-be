from flask import abort, request
from flask_restful import Resource

from service.resources.wikidata.utils import get_lexemes, search_lexeme_ids
from service.utils.languages import LanguageNotResolved, resolve_language
from service.utils.ll_filename import parse_ll_filename
from service.utils.matching import candidates_from_lexeme, sort_candidates
from service.utils.request_lang import get_ui_lang

MAX_FILES = 25


def _search_lang(language):
    return language.get("iso") or language.get("iso3")


def match_one_file(file_item, language):
    title = (file_item or {}).get("title") or ""
    word = (file_item or {}).get("word")
    if not word and title:
        word = parse_ll_filename(title).get("word")
    url = (file_item or {}).get("url")

    result = {
        "title": title or None,
        "word": word,
        "url": url,
        "candidates": [],
    }
    if not word:
        return result

    lang_code = _search_lang(language)
    found = search_lexeme_ids(word, lang_code)
    if isinstance(found, dict) and found.get("error"):
        result["error"] = found["error"]
        return result

    lexemes = get_lexemes(found)
    if isinstance(lexemes, dict) and lexemes.get("error"):
        result["error"] = lexemes["error"]
        return result

    candidates = []
    for lexeme in lexemes:
        candidates.extend(
            candidates_from_lexeme(
                lexeme,
                word,
                language.get("qid"),
                lang_code,
            )
        )
    result["candidates"] = sort_candidates(candidates)
    return result


def match_files(language, files):
    return [match_one_file(item, language) for item in files]


class MatchLexemesPost(Resource):
    def post(self):
        body = request.get_json(silent=True) or {}
        lang = body.get("lang")
        files = body.get("files")
        ui_lang = body.get("ui_lang") or get_ui_lang(request)

        if not lang or not isinstance(files, list):
            abort(400, "lang and files are required")
        if len(files) > MAX_FILES:
            abort(400, f"files cannot exceed {MAX_FILES} items")

        try:
            language = resolve_language(lang, ui_lang)
        except LanguageNotResolved as error:
            abort(400, str(error))

        return {
            "language": language,
            "results": match_files(language, files),
        }, 200
