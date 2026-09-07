from flask import abort
from flask_restful import Resource, fields, marshal_with, reqparse

from service import db
from service.models import UserModel
from service.require_token import token_required

user_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "pref_langs": fields.String,
}

user_args = reqparse.RequestParser()
user_args.add_argument("pref_langs", type=str)


class UserGet(Resource):
    @token_required
    @marshal_with(user_fields)
    def get(self, current_user, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "User not found")
        return user, 200


class UserPatch(Resource):
    @token_required
    @marshal_with(user_fields)
    def patch(self, current_user, id):
        if current_user.id != id:
            abort(403, "You can only update your own profile")
        args = user_args.parse_args()
        if args.get("pref_langs") is not None:
            current_user.pref_langs = args["pref_langs"]
            db.session.commit()
        return current_user, 200
