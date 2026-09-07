from flask import abort, g, request
from flask_restful import Resource

from service.resources.auth.utils import get_auth_object
from service.resources.wikidata.utils import add_pronunciation_audio
from service.require_token import token_required


class LexemeAudioAdd(Resource):
    @token_required
    def post(self, current_user):
        body = request.get_json(silent=True) or {}
        formid = body.get("formid")
        filename = body.get("filename")
        lang_wdqid = body.get("lang_wdqid")
        variety_qid = body.get("variety_qid")
        if not formid or not filename or not lang_wdqid:
            abort(400, "formid, filename, and lang_wdqid are required")

        auth_object = get_auth_object(getattr(g, "jwt_payload", None) or {})
        if not auth_object:
            abort(401, "OAuth access token is missing from the session")

        result = add_pronunciation_audio(
            current_user.username,
            auth_object,
            formid,
            filename,
            lang_wdqid,
            variety_qid,
        )
        if result.get("error"):
            abort(result.get("status_code", 503), result["error"])
        return result, 200
