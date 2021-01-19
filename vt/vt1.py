from flask import Blueprint, request

from vt.data import hello
from vt.helper import return_text

bp = Blueprint('vt1', __name__, url_prefix='/vt1')

@bp.route('/', methods=['GET'], strict_slashes=False)
@return_text
def res():
    name = request.args.get('name')
    return hello(name)