import logging
from os import killpg
from tupa.modules.helpers.decorators import sallitut_roolit

from flask.globals import current_app
from tupa.modules.services.data.dataservice import hae_kilpailut
from tupa.modules.helpers.forms import AdminLoginForm
from tupa.modules.helpers.auth import hashaa_salasana, tarkista_salasana
from tupa.modules.helpers.errors import AuthenticationError
from flask import Blueprint, session, redirect
from flask.helpers import url_for
from flask.templating import render_template
from tupa.modules.services.auth import redirect_to_auth_login, parse_user_from_token

bp = Blueprint('auth', __name__, url_prefix='')

# This will work as the login endpoint
@bp.route('/login', methods=['GET'])
def login():
    logging.debug("Login page requested.")

    # Generate the url where OAuth provider will send the auth token
    callback_url = url_for('auth.login_callback', _external=True)

    return redirect_to_auth_login(callback_url=callback_url)


# Logout endpoint
@bp.route('/logout', methods=['GET'])
def logout():
    logging.debug("Logout requested.")

    # Removes the user from the session, effectively logging them out
    session.pop('kayttaja', None)

    return redirect(url_for('index'))


# This will be used as the redirect address for OAuth
@bp.route('/login-callback', methods=['GET'])
def login_callback():
    logging.debug("Received callback from OAuth server")
    try:
        # Parses the user id and roles from the response. Authlib
        # grabs the token from the response context that does not have
        # to be passed explicitly.
        user = parse_user_from_token()
        user['roolit'] = ['perus']
        logging.info(f"Received token for: {user}")

        # Stores the user information in the session context. This will cause
        # flask to automatically return a session cookie that will be used to
        # id the user during further requests.
        session['kayttaja'] = user

        # If the user has admin status, redirect them to admin page after login
        # if 'admin' in user['roles']:
        #     return redirect(url_for("joukkueet."))

    except Exception as e:
        logging.error(f"Exception during authentication:")
        logging.error(e)

    return redirect(url_for('joukkueet.listaa'))


@bp.route('/admin/login', methods=['GET','POST'])
@sallitut_roolit(['perus'])
def admin_login():
    """Reitti, jonka kautta ylläpitäjät kirjautuvat sovellukseen"""

    if 'admin' in session['kayttaja']['roolit']:
        return redirect(url_for('joukkueet.listaa'))

    # luodaan kirjautumislomake
    kilpailut = hae_kilpailut()
    form = AdminLoginForm()
    arr_kilpailut = [(kilpailu.key.id, kilpailu['nimi']) for kilpailu in kilpailut]
    form.kilpailu.choices = arr_kilpailut

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

            # tallennetaan sessioon tieto valinnoista
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
    print("poistutaan admin-tilasta")
    # poistetaan admin käyttäjän rooleista
    # ei tarvitse try exceptiä kun pääsy on rajattu vain admineille
    kayttaja = session['kayttaja']
    kayttaja['roolit'].remove('admin')
    session['kayttaja'] = kayttaja


    # ohjataan takaisin kilpailulistaukseen
    return redirect(url_for('joukkueet.listaa'))