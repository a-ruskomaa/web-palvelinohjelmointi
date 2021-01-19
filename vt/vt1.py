from flask import Blueprint, request

from vt.data import download_data, parse_teams, names_to_string, generate_random_id
from vt.helper import return_text

bp = Blueprint('vt1', __name__, url_prefix='/vt1')

@bp.route('/', methods=['GET'], strict_slashes=False)
@return_text
def res():
    rows = []
    rows.append("----------- TASO 1 -----------")
    # virheenkäsittely
    data = download_data()
    teams = parse_teams(data)
    rows.append(names_to_string(teams))

    rows.append("random ID: " + str(generate_random_id(teams)))

    return "\n".join(rows)