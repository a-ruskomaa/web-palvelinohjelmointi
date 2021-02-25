import os
from flask import Flask, render_template, session
from flask.helpers import url_for
from werkzeug.utils import redirect

print("initializing app...")

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile(os.path.join('config', 'config.py'))
    
    print("creating app...")

    from tupa.modules.data import db
    db.init_app(app)

    from .views import admin, auth, joukkueet
    app.register_blueprint(admin.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(joukkueet.bp)

    @app.route('/', methods=["GET"])
    def index():
        kayttaja = session.get('kayttaja', None)
        if kayttaja and 'joukkue' in kayttaja['roolit']:
            return redirect(url_for('joukkueet.listaa'))
        elif kayttaja and 'admin' in kayttaja['roolit']:
            return redirect(url_for('admin.listaa'))
        else:
            return redirect(url_for('auth.login'))
            
    return app