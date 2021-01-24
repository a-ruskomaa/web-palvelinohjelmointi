from flask import Blueprint, request

from vt.data.data import load_data, save_data
from vt.data.teams import parse_teams, add_team, remove_team, names_to_string, calculate_points, Joukkue
from vt.data.checkpoints import checkpoints_to_string
from vt.data.series import get_series_by_name
from vt.helper import return_text

bp = Blueprint('vt1', __name__, url_prefix='/vt1')

@bp.route('/', methods=['GET'], strict_slashes=False)
@return_text
def res():
    """Muodostaa tekstimuotoisen vastauksen get-pyyntöön"""
    rows = []

    # Haetaanko data paikallisesta vai ulkoisesta tiedostosta
    reset_data = bool(request.args.get('reset', 0))
    data = load_data(remote=reset_data)
    
    # Tarkistetaan onko pyynnön argumentteina joukkueen tiedot
    parsed = parse_team_from_arguments(request.args, data)
    if parsed:
        tila = request.args.get('tila', 'insert')
        if tila == 'insert':
            add_team(parsed[0], parsed[1].__dict__)
        elif tila == 'delete':
            remove_team(parsed[0], parsed[1].nimi)
        save_data(data)

    rows.append(stage1_response(data))
    rows.append("")
    rows.append(stage3_response(data))
    rows.append("")

    return "\n".join(rows)


def parse_team_from_arguments(args, data):
    """Muodostaa argumentteina annetuista tiedosta joukkue-objektin"""
    name = request.args.get('nimi')
    series_name = request.args.get('sarja')
    if name and series_name:
        series = get_series_by_name(series_name, data)
        if series:
            members = request.args.getlist('jasen')
            team = Joukkue(nimi=name, jasenet=members)

            return (series, team)
    return None


def stage1_response(data):
    """Muodostaa 1-tason vastauksen"""
    rows = []
    rows.append("----------- TASO 1 -----------")
    # TODO virheenkäsittely
    teams = parse_teams(data)
    rows.append(names_to_string(teams))

    rows.append("")

    rows.append(checkpoints_to_string(data['rastit']))

    return "\n".join(rows)


def stage3_response(data):
    """Muodostaa 3-tason vastauksen"""
    rows = []
    rows.append("----------- TASO 3 -----------")

    checkpoints = data['rastit']
    
    # Hirveä onelineri, joka luo jokaisesta joukkueesta tuplen muotoa (pisteet, nimi, jäsenet[])
    # ja järjestää joukkueet ensisijaisesti pisteiden mukaan, toissijaisesti nimen mukaan
    teams = sorted(((calculate_points(team, checkpoints), team['nimi'], sorted(team['jasenet'])) for team in parse_teams(data)), key=lambda x:(-x[0],x[1]))

    # Tulostellaan jokaisen joukkueen ja jäsenen tiedot
    for team in teams:
        rows.append(f"{team[1]} ({team[0]})")
        for member in team[2]:
            rows.append(f"  {member}")

    
    return "\n".join(rows)

