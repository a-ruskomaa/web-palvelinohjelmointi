import os
import logging
from flask import Flask, render_template, session
from flask.helpers import url_for
from werkzeug.utils import redirect


def create_app():
    app = Flask(__name__)

    # ladataan asetukset (mm. tietokannan osoite) tiedostosta
    path_to_config = os.path.join(os.getcwd(),'config', 'config.py')
    app.config.from_pyfile(path_to_config)

    # alustetaan tietokanta
    from tupa.modules.data import db
    db.init_app(app)

    # rekisteröidään reitit
    from tupa.modules.blueprints import admin, auth, joukkueet
    app.register_blueprint(admin.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(joukkueet.bp)

    @app.route('/', methods=["GET"])
    def index():
        # haetaan käyttäjän tiedot sessiosta
        kayttaja = session.get('kayttaja', None)

        # ohjataan kirjautunut käyttäjä roolin mukaiselle aloitussivulle ja
        # kirjautumaton käyttäjä kirjautumissivulle
        if kayttaja and 'joukkue' in kayttaja['roolit']:
            return redirect(url_for('joukkueet.listaa'))
        elif kayttaja and 'admin' in kayttaja['roolit']:
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('auth.login'))
            
    return app