import os

from flask import Flask, request


def create_app(test_config=None):
    # create and configure the app
    # app = Flask(__name__, instance_relative_config=True)
    app = Flask(__name__)

    # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    # rekisteröidään viikkotehtävien polut blueprinteina selkeyttämään koodia
    from . import vt1
    app.register_blueprint(vt1.bp)

    return app