from flask import Blueprint, request

from . import data

bp = Blueprint('vt1', __name__, url_prefix='/vt1')

@bp.route('/', methods=['GET'], strict_slashes=False)
def hello():
    name = request.args.get('name')
    return data.hello(name)