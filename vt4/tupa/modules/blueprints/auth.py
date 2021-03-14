import logging
from flask.globals import current_app
from tupa.modules.services.data import ds
from tupa.modules.services.auth import authService
from tupa.modules.helpers.forms import AdminLoginForm
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.auth import tarkista_salasana
from tupa.modules.helpers.errors import AuthenticationError
from flask import Blueprint, session, redirect
from flask.helpers import url_for
from flask.templating import render_template

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/login', methods=['GET'])
def login():
    """ Polku sisäänkirjautumista varten """
    logging.debug("Login page requested.")

    # Luodaan url oauth-palvelimen takaisinkutsua varten
    callback_url = url_for('auth.login_callback', _external=True)

    # uudelleenohjataan autentikaatiopalvelimelle
    return authService.redirect_to_auth_login(callback_url=callback_url)


@bp.route('/logout', methods=['GET'])
def logout():
    """ Polku uloskirjautumista varten varten """
    logging.debug("Logout requested.")

    # poistetaan käyttäjä sessiosta, joka estää pääsyn kirjautumista vaativille sivuille
    session.pop('kayttaja', None)

    # ohjataan takaisin etusivulle
    return redirect(url_for('index'))


@bp.route('/login-callback', methods=['GET'])
def login_callback():
    """ Polku autentikaatiopalvelimen takaisinkutsua varten """
    logging.debug("Received callback from OAuth server")
    try:
        # parsitaan käyttäjän tiedot tokenista
        user = authService.parse_user_from_token()
        logging.info(f"Received token for: {user}")
        
        # lisätään peruskäyttäjän oikeudet ja tallennetaan käyttäjä sessioon
        user['roolit'] = ['perus'] 
        session['kayttaja'] = user

    except Exception as e:
        logging.error(f"Exception during authentication:")
        logging.error(e)

    return redirect(url_for('joukkueet.listaa'))


@bp.route('/admin/login', methods=['GET','POST'])
@sallitut_roolit(['perus'])
def admin_login():
    """ Ylläpitäjän sisäänkirjautumissivu """

    kilpailut = ds.hae_kilpailut()

    if len(kilpailut) == 0:
        return redirect(url_for('joukkueet.listaa'))

    # luodaan kilpailukohtainen kirjautumislomake
    form = AdminLoginForm()

    # lisätään kilpailut valinnoiksi
    arr_kilpailut = [(kilpailu.key.id, kilpailu['nimi']) for kilpailu in kilpailut]
    form.kilpailu.choices = arr_kilpailut

    # valitaan tarvittaessa ensimmäinen kilpailu valmiiksi
    if not form.kilpailu.data:
        form.kilpailu.data = arr_kilpailut[0][0]

    loginerrors = []

    # tarkistetaan formi
    if form.validate_on_submit():
        try:
            # haetaan hyväksytyt adminin tunnukset asetuksista
            id = current_app.config['ADMIN_ID']
            pw_hash = current_app.config['ADMIN_PW_HASH']

            # funktio heittää AuthenticationError:n jos salasana on väärä
            tarkista_salasana(pw_hash, form.salasana.data, id)

            # tallennetaan käyttäjän tiedot sessioon
            kayttaja = session['kayttaja']
            kayttaja['roolit'].append('admin')
            session['kayttaja'] = kayttaja

            # tallennetaan sessioon tieto valitusta kilpailusta
            session['kilpailu'] = form.kilpailu.data

            # ohjataan sisäänkirjautumisen jälkeen kilpailulistaukseen
            return redirect(url_for('joukkueet.listaa'))

        except (AuthenticationError):
            # näytetään käyttäjälle virheilmoitus jos salasana on väärä
            loginerrors.append('Kirjautuminen epäonnistui')
    
    # näytetään kirjautumissivu
    return render_template('admin/admin_login.html', form=form, loginerrors=loginerrors)



@bp.route('/admin/logout', methods=['GET','POST'])
@sallitut_roolit(['admin'])
def admin_logout():
    """ Ylläpitäjän uloskirjautuminen """

    # poistetaan admin käyttäjän rooleista
    # ei tarvitse try exceptiä kun pääsy on rajattu vain admineille
    kayttaja = session['kayttaja']
    kayttaja['roolit'].remove('admin')
    session['kayttaja'] = kayttaja

    # poistetaan myös tieto valitusta kilpailusta
    session.pop('kilpailu')

    # ohjataan takaisin kilpailulistaukseen
    return redirect(url_for('joukkueet.listaa'))