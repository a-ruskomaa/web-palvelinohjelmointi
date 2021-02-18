from urllib.error import URLError
from flask import Blueprint, request

import tupa.modules.data.db
from tupa.modules.domain.teams import parse_teams, create_team, add_team, remove_team, update_team, names_to_string
from tupa.modules.domain.statistics import calculate_statistics
from tupa.modules.domain.checkpoints import checkpoints_to_string
from tupa.modules.domain.series import get_series_by_name
from tupa.helpers.decorators import return_text

vt3 = Blueprint('vt3', __name__, url_prefix='/vt3')

@vt3.route('/', methods=['GET'], strict_slashes=False)
def index():
    return "Hello!"