from flask import Blueprint
from flask.globals import request
from flask.helpers import make_response
from firebase_admin import auth as firebase_auth
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='')

def auth_required(func):
    """Sallii vain annetuissa rooleissa oleville käyttäjille pääsyn tällä koristeltuun reittiin."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = parse_jwt(request.headers['Authorization'])
            print(token)
            dict = firebase_auth.verify_id_token(token)
            print(dict)
        except Exception as error:
            print(error)

        return func(*args, **kwargs)
    return wrapper

def parse_jwt(header: str):
    if not header.startswith('Bearer '):
        return None
    return header.replace('Bearer ', '')

@bp.route('/auth_test', methods=['GET'])
@auth_required
def test_auth():
    print(request.headers['Authorization'])
    return make_response({'status': 'OK'}, 200)
