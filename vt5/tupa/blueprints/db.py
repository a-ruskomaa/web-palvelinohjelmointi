from flask import Blueprint, json
from flask.globals import request
from flask.helpers import make_response
from firebase_admin import firestore
from tupa.blueprints.auth import auth_required

bp = Blueprint('db', __name__, url_prefix='')


@bp.route('/kilpailut/<kilpailu_id>', methods=['GET'])
@auth_required
def get_kilpailu(kilpailu_id: str):
    db = firestore.client()

    print(request.headers['Authorization'])
    return make_response({'status': 'OK'}, 200)


@bp.route('/kilpailut/<kilpailu_id>/sarjat', methods=['GET'])
# @auth_required
def get_kilpailu_sarjat(kilpailu_id: str):
    db = firestore.client()

    sarjat_dict = {}

    sarjat = db.collection(f"kilpailut/{kilpailu_id}/sarjat").stream()

    for sarja in sarjat:
        sarjat_dict[sarja.id] = sarja.to_dict()


    return make_response(sarjat_dict, 200)


@bp.route('/kilpailut/<kilpailu_id>/rastit', methods=['GET'])
# @auth_required
def get_kilpailu_rastit(kilpailu_id: str):
    db = firestore.client()

    rastit_dict = {}

    rastit = db.collection(f"kilpailut/{kilpailu_id}/rastit").stream()

    for rasti in rastit:
        rastit_dict[rasti.id] = rasti.to_dict()

    return make_response(rastit_dict, 200)
