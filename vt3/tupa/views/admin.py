from urllib.error import URLError
from flask import Blueprint, request, render_template

import tupa.modules.data.db
from tupa.helpers.decorators import return_text

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'], strict_slashes=False)
def index():
    return render_template('admin/index.html')