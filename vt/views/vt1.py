from urllib.error import URLError
from flask import Blueprint, request

from vt.modules.data import load_data, save_data
from vt.modules.teams import parse_teams, create_team, add_team, remove_team, update_team, names_to_string
from vt.modules.statistics import calculate_statistics
from vt.modules.checkpoints import checkpoints_to_string
from vt.modules.series import get_series_by_name
from vt.helpers.decorators import return_text

vt1 = Blueprint('vt1', __name__, url_prefix='/vt1')

@vt1.route('/', methods=['GET'], strict_slashes=False)
@return_text
def res():
    """Muodostaa tekstimuotoisen vastauksen get-pyyntöön"""
    rows = []
    
    # Päätetään argumenttien perusteella luetaanko data paikallisesta tietorakenteesta vai palvelimelta
    reset_data = bool(request.args.get('reset', 0))

    # Ladataan data, käsitellään todennäköisimmät virhetapaukset
    try:
        data = load_data(remote=reset_data)
    except URLError:
        return "Palvelin ei vastaa"
    except FileNotFoundError:
        return "Tiedostoa ei löydy"

    # Luetaan pyynnön loput argumentit
    state, team, series = parse_arguments(request.args, data)

    # Käsitellään argumenttien dataa asiaankuuluvalla tavalla
    if series and state == 'insert':
        add_team(series, team)
        save_data(data)
    elif series and state == 'delete':
        remove_team(series, team['nimi'])
        save_data(data)
    elif state == 'update':
        update_team(data, series, team)
        save_data(data)

    # Lisätään vastaukseen tasokohtaiset tulostukset
    rows.append(stage1_response(data))
    rows.append("")
    rows.append(stage3_response(data))
    rows.append("")
    rows.append(stage5_response(data))
    rows.append("")

    return "\n".join(rows)


def parse_arguments(args, data):
    """Parsii argumenteista joukkueiden käsittelyyn tarvittavan datan ja palauttaa sen sopivassa muodossa"""
    state = args.get('tila', 'insert')
    team_name = args.get('nimi')
    series_name = args.get('sarja')
    team_id = args.get('id', -1, type=int)
    team = None
    series = None

    # Jos on annettu sarjan nimi, yritetään etsiä nimeä vastaava sarja
    if series_name:
        series = get_series_by_name(series_name, data)

    # Jos on annettu joukkueen nimi, luodaan joukkuetta vastaava dictionary
    if team_name:
        members = args.getlist('jasen')
        punching_methods = [data['leimaustapa'].index(x) for x in args.getlist('leimaustapa')]
        team = create_team(team_name, members, team_id, punching_methods)

    return state, team, series


def stage1_response(data):
    """Muodostaa 1-tason vastauksen"""
    rows = []
    rows.append("----------- TASO 1 -----------")

    # Muodostetaan kaikista joukkueista merkkijono
    rows.append(names_to_string(parse_teams(data)))

    rows.append("")

    # Muodostetaan kaikista rasteista merkkijono
    rows.append(checkpoints_to_string(data['rastit']))

    return "\n".join(rows)


def stage3_response(data):
    """Muodostaa 3-tason vastauksen"""
    rows = []
    rows.append("----------- TASO 3 -----------")

    checkpoints = data['rastit']
    
    # Hirveä onelineri, joka luo jokaisesta joukkueesta tuplen muotoa (pisteet, nimi, jäsenet[])
    # ja järjestää joukkueet ensisijaisesti pisteiden mukaan, toissijaisesti nimen mukaan
    teams = sorted(((calculate_statistics(team, checkpoints)[0], team['nimi'], sorted(team['jasenet'])) for team in parse_teams(data)), key=lambda x:(-x[0],x[1]))

    # Tulostellaan jokaisen joukkueen ja jäsenen tiedot
    for points, name, members in teams:
        rows.append(f"{name} ({points} p)")
        for member in members:
            rows.append(f"  {member}")

    
    return "\n".join(rows)


def stage5_response(data):
    """Muodostaa 5-tason vastauksen"""
    rows = []
    rows.append("----------- TASO 5 -----------")

    checkpoints = data['rastit']
    
    # Hirveä onelineri, joka luo jokaisesta joukkueesta tuplen muotoa (pisteet, aika, etäisyys, nimi, jäsenet[])
    # ja järjestää joukkueet ensisijaisesti pisteiden, toissijaisesti ajan mukaan
    teams = sorted(((*calculate_statistics(team, checkpoints), team['nimi'], sorted(team['jasenet'])) for team in parse_teams(data)), key=lambda x:(-x[0],x[1]))

    # Tulostellaan jokaisen joukkueen ja jäsenen tiedot
    for points, time, distance, name, members in teams:
        rows.append(f"{name} ({points} p, {int(round(distance))} km, {time})")
        for member in members:
            rows.append(f"  {member}")

    
    return "\n".join(rows)