from flask import redirect

from service import app, api, prefix
from service.resources.commons.commons import CommonsFileUrlGet, CommonsFilesGet
from service.resources.health.health import HealthGet
from service.resources.languages.languages import LanguageGet, LanguagesGet
from service.resources.matching.matching import MatchLexemesPost
from swagger.swaggerConfig import SwaggerConfig

api.add_resource(SwaggerConfig, "/swagger-config")
api.add_resource(HealthGet, "/health")
api.add_resource(LanguagesGet, "/languages")
api.add_resource(LanguageGet, "/languages/<string:lang_code>")
api.add_resource(CommonsFilesGet, "/commons/files")
api.add_resource(CommonsFileUrlGet, "/file/url/<path:titles>")
api.add_resource(MatchLexemesPost, "/match-lexemes")


@app.route("/")
def redirect_to_prefix():
    return redirect(prefix)


if __name__ == "__main__":
    app.run(debug=True)
