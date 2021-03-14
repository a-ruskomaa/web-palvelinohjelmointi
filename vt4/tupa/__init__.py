import os
from flask import Flask, render_template, session, redirect
from flask.helpers import url_for


def create_app():
    app = Flask(__name__)

    # ladataan asetukset tiedostosta
    path_to_config = os.path.join(os.getcwd(),'config', 'config.py')
    app.config.from_pyfile(path_to_config)

    # alustetaan tietokanta
    from tupa.modules.services.data import db, ds
    db.init_app(app)

    # alustetaan autentikaatio
    from tupa.modules.services.auth import oauth, authService
    oauth.init_app(app)
    authService.init_app(app)

    # rekisteröidään reitit
    from tupa.modules.blueprints import auth, joukkueet, rastit, leimaukset
    app.register_blueprint(auth.bp)
    app.register_blueprint(joukkueet.bp)
    app.register_blueprint(rastit.bp)
    app.register_blueprint(leimaukset.bp)

    # injektoidaan käyttäjän roolit automaattisesti jinjan käyttöön
    @app.context_processor
    def inject_roles():
        kayttaja = session.get('kayttaja')
        if kayttaja:
            return dict(roles=kayttaja['roolit'])
        return {}

    # injektoidaan valittu kilpailu automaattisesti jinjan käyttöön
    @app.context_processor
    def inject_selection():
        valittu_kilpailu = session.get('kilpailu')
        if valittu_kilpailu:
            kilpailu = ds.hae_kilpailu(int(valittu_kilpailu))
            valittu_kilpailu_nimi = None
            if kilpailu:
                valittu_kilpailu_nimi = kilpailu['nimi']
            return dict(valittu_kilpailu=valittu_kilpailu, valittu_kilpailu_nimi=valittu_kilpailu_nimi)
        return {}


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