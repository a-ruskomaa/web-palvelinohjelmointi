from flask.globals import request
from flask.helpers import make_response
from firebase_admin import auth as firebase_auth
from functools import wraps


def auth_required(func):
    """Sallii vain tunnistautuneilta käyttäjiltä pääsyn kyseiseen reittiin."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = parse_jwt(request.headers['Authorization'])
            print(token)
            dict = firebase_auth.verify_id_token(token)
            print(dict)
            return func(*args, **kwargs)
        except KeyError as error:
            print(error)
            return make_response({'status': 'Unauthorized'}, 403)
        except (ValueError, firebase_auth.InvalidIdTokenError) as error:
            print(error)
            return make_response({'status': 'Invalid ID-token'}, 401)
        except (firebase_auth.ExpiredIdTokenError, firebase_auth.RevokedIdTokenError) as error:
            print(error)
            return make_response({'status': 'ID-token is no longer valid'}, 401)
        except Exception as error:
            print(error)
            return make_response({'status': 'Something went wrong'}, 500)
    return wrapper

def parse_jwt(header: str):
    if not header.startswith('Bearer '):
        return None
    return header.replace('Bearer ', '')

