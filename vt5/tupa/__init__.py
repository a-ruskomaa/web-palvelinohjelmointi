import os
import firebase_admin
from flask import Flask, render_template
# from flask.helpers import make_response
from flask_cors import CORS

default_app = firebase_admin.initialize_app()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ladataan asetukset tiedostosta
    path_to_config = os.path.join(os.getcwd(), 'config', 'config.py')
    app.config.from_pyfile(path_to_config)

    from tupa.blueprints import init_db, db
    app.register_blueprint(init_db.bp)
    app.register_blueprint(db.bp)

    # @app.route('/', methods=["GET"])
    # def index():
    #     resp = make_response(render_template("index.xhtml"))
    #     resp.headers['Content-type'] = 'application/xhtml+xml;charset=UTF-8'
    #     return resp

    return app
