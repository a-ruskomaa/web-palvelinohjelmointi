import os
from flask import Flask, render_template
from flask.helpers import make_response


def create_app():
    app = Flask(__name__)

    # ladataan asetukset tiedostosta
    path_to_config = os.path.join(os.getcwd(), 'config', 'config.py')
    app.config.from_pyfile(path_to_config)

    # alustetaan tietokanta
    # from tupa.modules.services.data import db, ds
    # db.init_app(app)

    # alustetaan autentikaatio
    # from tupa.modules.services.auth import oauth, authService
    # oauth.init_app(app)
    # authService.init_app(app)

    @app.route('/', methods=["GET"])
    def index():
        resp = make_response(render_template("index.xhtml"))
        resp.headers['Content-type'] = 'application/xhtml+xml;charset=UTF-8'
        return resp

    return app
