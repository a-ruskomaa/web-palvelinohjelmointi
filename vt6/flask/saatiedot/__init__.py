import os
import firebase_admin
from flask import Flask, render_template
# from flask.helpers import make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

db = SQLAlchemy()
default_app = firebase_admin.initialize_app()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ladataan asetukset tiedostosta
    path_to_config = os.path.join(os.getcwd(), 'config', 'config.py')
    app.config.from_pyfile(path_to_config)

    # rekisteröidään tietokanta
    db.init_app(app)

    # alustetaan välimuisti
    cache.init_app(app)

    from saatiedot.blueprints import api
    app.register_blueprint(api.bp)

    @app.route('/', methods=["GET"])
    def index():
        return "hello", 200

    return app
