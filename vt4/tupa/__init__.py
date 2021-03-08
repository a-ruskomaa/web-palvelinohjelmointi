import os
from flask import Flask, render_template, session, redirect
from flask.helpers import url_for


def create_app():
    app = Flask(__name__)

    # ladataan asetukset (mm. tietokannan osoite) tiedostosta
    path_to_config = os.path.join(os.getcwd(),'config', 'config.py')
    app.config.from_pyfile(path_to_config)

    # alustetaan tietokanta
    from tupa.modules.services.data import db
    db.init_app(app)

    # alustetaan autentikaatio
    from tupa.modules.services.auth import init_auth
    init_auth(app)

    # rekisteröidään reitit
    from tupa.modules.blueprints import admin, auth, joukkueet, rastit, leimaukset
    app.register_blueprint(admin.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(joukkueet.bp)
    app.register_blueprint(rastit.bp)
    app.register_blueprint(leimaukset.bp)

    # näytetään virhesivu jos tietokantakutsu aiheuttaa virhetilanteen
    # app.register_error_handler(mysql.connector.Error, lambda: render_template('common/error.html', message="Jotain meni pieleen..."))

    @app.route('/', methods=["GET"])
    def index():
        # haetaan käyttäjän tiedot sessiosta
        kayttaja = session.get('kayttaja', None)

        # ohjataan kirjautunut käyttäjä aloitussivulle ja
        # kirjautumaton käyttäjä kirjautumissivulle
        if kayttaja:
            return redirect(url_for('joukkueet.listaa'))
        else:
            return render_template('index.html')
            
    return app