from collections import namedtuple
import pprint
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.services.data.dataservice import hae_joukkue, hae_joukkueet, hae_kilpailu, hae_sarjat, hae_kilpailut, lisaa_joukkue, paivita_joukkue, poista_joukkue
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import LisaysForm, MuokkausForm

bp = Blueprint('leimaukset', __name__, url_prefix='/leimaukset')

@bp.route('/lisaa', methods=['GET', 'POST'], strict_slashes=False)
@sallitut_roolit(['perus', 'admin'])
def lisaa():
    pass