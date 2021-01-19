from flask import Blueprint, request

from vt.data.data import load_data, save_data
from vt.data.teams import parse_teams, add_team, names_to_string, Joukkue
from vt.data.checkpoints import checkpoints_to_string
from vt.data.series import get_series_by_name
from vt.helper import return_text

bp = Blueprint('vt1', __name__, url_prefix='/vt1')

@bp.route('/', methods=['GET'], strict_slashes=False)
@return_text
def res():
    rows = []

    data = load_data()
    
    parsed = parse_team_from_arguments(request.args, data)
    if parsed:
        add_team(parsed[0], parsed[1].__dict__)
        save_data(data)

    rows.append(vt1_response(data))

    return "\n".join(rows)


def parse_team_from_arguments(args, data):
    name = request.args.get('nimi')
    series_name = request.args.get('sarja')
    if name and series_name:
        series = get_series_by_name(series_name, data)
        if series:
            members = request.args.getlist('jasen')
            team = Joukkue(nimi=name, jasenet=members)

            return (series, team)
    return None


def vt1_response(data):
    rows = []
    rows.append("----------- TASO 1 -----------")
    # virheenkäsittely
    teams = parse_teams(data)
    rows.append(names_to_string(teams))

    rows.append("\n")

    rows.append(checkpoints_to_string(data['rastit']))

    return "\n".join(rows)