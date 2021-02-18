from urllib.error import URLError
from flask import Blueprint, request

import tupa.modules.data.db
from tupa.helpers.decorators import return_text

vt3 = Blueprint('vt3', __name__, url_prefix='/vt3')

@vt3.route('/', methods=['GET'], strict_slashes=False)
def index():
    return "Hello!"