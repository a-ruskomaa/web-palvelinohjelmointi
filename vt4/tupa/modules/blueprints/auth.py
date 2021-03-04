import logging
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
    session.pop('user')

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
        logging.info(f"Received token for: {user}")

        # Stores the user information in the session context. This will cause
        # flask to automatically return a session cookie that will be used to
        # id the user during further requests.
        session['user'] = user

        # If the user has admin status, redirect them to admin page after login
        # if 'admin' in user['roles']:
        #     return redirect(url_for("joukkueet."))

    except Exception as e:
        logging.error(f"Exception during authentication:")
        logging.error(e)

    # return redirect(url_for('home'))
    return render_template('common/login.html', user = session.get('user'))


