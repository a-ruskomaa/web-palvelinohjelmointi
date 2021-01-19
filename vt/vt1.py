from flask import Blueprint, request

from vt.data import (
    load_data,
    parse_teams,
    names_to_string,
    generate_random_id,
    checkpoints_to_string)
from vt.helper import return_text

bp = Blueprint('vt1', __name__, url_prefix='/vt1')

@bp.route('/', methods=['GET'], strict_slashes=False)
@return_text
def res():
    data = load_data()
    return vt1_response(data)

def vt1_response(data):
    rows = []
    rows.append("----------- TASO 1 -----------")
    # virheenkäsittely
    data = load_data()
    teams = parse_teams(data)
    rows.append(names_to_string(teams))

    rows.append("\n")

    rows.append(checkpoints_to_string(data['rastit']))

    return "\n".join(rows)