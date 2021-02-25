from flask import Blueprint, render_template
from flask import redirect, request
from tupa.modules.data.dataservice import hae_kilpailut, hae_sarjat, hae_joukkueet

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'], strict_slashes=False)
def index():
    return redirect('admin/kilpailut')


@bp.route('/kilpailut', methods=['GET'], strict_slashes=False)
def listaa_kilpailut():
    kilpailut = hae_kilpailut()
    return render_template('admin/lista.html', items=kilpailut, urlstring='admin.listaa_sarjat')


@bp.route('/sarjat', methods=['GET'], strict_slashes=False)
def listaa_sarjat():
    sarjat = hae_sarjat(kilpailu_id=request.args.get('id'))
    return render_template('admin/lista.html', items=sarjat, urlstring='admin.listaa_joukkueet')


@bp.route('/joukkueet', methods=['GET'], strict_slashes=False)
def listaa_joukkueet():
    joukkueet = hae_joukkueet(sarja_id=request.args.get('id'))
    return render_template('admin/lista.html', items=joukkueet, urlstring='index')