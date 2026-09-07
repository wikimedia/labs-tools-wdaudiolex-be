import argparse

from flask import redirect

from common import port as default_port
from service import app, api, db, prefix
from service.models import ContributionModel, UserModel  # noqa: F401
from service.resources.auth.auth import AuthCallBackPost, AuthGet, AuthLogout
from service.resources.commons.commons import CommonsFileUrlGet, CommonsFilesGet
from service.resources.contributions.contribution import ContributionsGet
from service.resources.health.health import HealthGet
from service.resources.languages.languages import LanguageGet, LanguagesGet
from service.resources.matching.matching import MatchLexemesPost
from service.resources.users.users import UserGet, UserPatch
from service.resources.wikidata.lexeme import LexemeAudioAdd
from swagger.swaggerConfig import SwaggerConfig

api.add_resource(SwaggerConfig, "/swagger-config")
api.add_resource(HealthGet, "/health")
api.add_resource(AuthGet, "/auth/login")
api.add_resource(AuthCallBackPost, "/oauth-callback")
api.add_resource(AuthLogout, "/auth/logout")
api.add_resource(LanguagesGet, "/languages")
api.add_resource(LanguageGet, "/languages/<string:lang_code>")
api.add_resource(CommonsFilesGet, "/commons/files")
api.add_resource(CommonsFileUrlGet, "/file/url/<path:titles>")
api.add_resource(MatchLexemesPost, "/match-lexemes")
api.add_resource(LexemeAudioAdd, "/lexeme/audio/add")
api.add_resource(ContributionsGet, "/contributions")
api.add_resource(UserGet, "/users/<int:id>")
api.add_resource(UserPatch, "/users/<int:id>")


@app.route("/")
def redirect_to_prefix():
    return redirect(prefix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WDAudioLex API")
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=int(default_port),
        help="Port to listen on (default: PORT from .env, or 5000)",
    )
    args = parser.parse_args()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=args.port)
