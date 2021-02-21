from flask import Blueprint, render_template

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'], strict_slashes=False)
def index():
    return render_template('admin/index.html')