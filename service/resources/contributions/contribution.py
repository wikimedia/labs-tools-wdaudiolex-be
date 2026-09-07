from flask import request
from flask_restful import Resource, fields, marshal_with

from service.models import ContributionModel
from service.require_token import optional_token

contribution_fields = {
    "id": fields.Integer,
    "wd_item": fields.String,
    "form_id": fields.String,
    "username": fields.String,
    "lang_code": fields.String,
    "audio_filename": fields.String,
    "variety_qid": fields.String,
    "edit_type": fields.String,
    "data": fields.String,
    "revision_id": fields.String,
    "date": fields.DateTime(dt_format="iso8601"),
}


class ContributionsGet(Resource):
    @optional_token
    @marshal_with(contribution_fields)
    def get(self, current_user):
        query = ContributionModel.query
        username = request.args.get("username")
        lang_code = request.args.get("lang_code")
        if username:
            query = query.filter_by(username=username)
        if lang_code:
            query = query.filter_by(lang_code=lang_code)
        return query.order_by(ContributionModel.date.desc()).limit(100).all()
