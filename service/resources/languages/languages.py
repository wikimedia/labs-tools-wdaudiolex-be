from flask import abort, request
from flask_restful import Resource, fields, marshal_with

from service.utils.languages import LanguageNotResolved, list_languages, resolve_language
from service.utils.request_lang import get_ui_lang

language_fields = {
    "iso": fields.String,
    "iso3": fields.String,
    "qid": fields.String,
    "label": fields.String,
    "commons_category": fields.String,
}


class LanguagesGet(Resource):
    @marshal_with(language_fields)
    def get(self):
        return list_languages(get_ui_lang(request))


class LanguageGet(Resource):
    @marshal_with(language_fields)
    def get(self, lang_code):
        try:
            return resolve_language(lang_code, get_ui_lang(request))
        except LanguageNotResolved as error:
            abort(400, str(error))
