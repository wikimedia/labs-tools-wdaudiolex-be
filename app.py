from flask import redirect

from service import app, api, prefix
from service.resources.health.health import HealthGet
from swagger.swaggerConfig import SwaggerConfig

api.add_resource(SwaggerConfig, "/swagger-config")
api.add_resource(HealthGet, "/health")


@app.route("/")
def redirect_to_prefix():
    return redirect(prefix)


if __name__ == "__main__":
    app.run(debug=True)
