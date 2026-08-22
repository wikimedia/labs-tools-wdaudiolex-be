from flask import abort, request
from flask_restful import Resource, reqparse

from service.resources.commons.utils import get_file_url, list_lingua_libre_files
from service.utils.languages import LanguageNotResolved, resolve_language
from service.utils.request_lang import get_ui_lang

files_args = reqparse.RequestParser()
files_args.add_argument("lang", type=str, required=True, location="args")
files_args.add_argument("continue", type=str, location="args", dest="continue_token")
files_args.add_argument("limit", type=int, location="args", default=50)
files_args.add_argument("speaker", type=str, location="args")
files_args.add_argument("ui_lang", type=str, location="args")


class CommonsFilesGet(Resource):
    def get(self):
        args = files_args.parse_args()
        limit = args["limit"] or 50
        if limit < 1 or limit > 100:
            abort(400, "limit must be between 1 and 100")

        ui_lang = args["ui_lang"] or get_ui_lang(request)
        try:
            language = resolve_language(args["lang"], ui_lang)
        except LanguageNotResolved as error:
            abort(400, str(error))

        result = list_lingua_libre_files(
            language["iso3"],
            continue_token=args["continue_token"],
            limit=limit,
        )
        if result.get("error") and result.get("status_code"):
            abort(result["status_code"], result["error"])

        speaker = (args["speaker"] or "").strip().lower()
        files = result.get("files", [])
        if speaker:
            files = [
                item for item in files
                if item.get("speaker") and speaker in item["speaker"].lower()
            ]

        return {
            "language": language,
            "files": files,
            "continue": result.get("continue"),
        }, 200


class CommonsFileUrlGet(Resource):
    def get(self, titles):
        result = get_file_url(titles)
        if result.get("error") and result.get("status_code"):
            abort(result["status_code"], result["error"])
        return result, 200
