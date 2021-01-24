import random
from datetime import date, datetime
from vt.data.data import load_data
from vt.data.checkpoints import find_checkpoint_by_id, get_points

class Joukkue:
    def __init__(self, nimi: str, jasenet: list=[], id: int=-1,  leimaustapa: list=[], rastit: list=[]):
        self.nimi = nimi
        self.jasenet = jasenet
        self.id = id
        self.leimaustapa = leimaustapa
        self.rastit = rastit

    def __str__(self) -> str:
        return str(self.__dict__)


def parse_teams(data: dict):
    """Parsii datasta kaikki joukkueet tiedot ja palauttaa ne listalla"""
    teams = []

    for sarja in data['sarjat']:
        for joukkue in sarja['joukkueet']:
            teams.append(joukkue)

    return teams


def names_to_string(teams: list):
    """Muodostaa joukkueiden nimistä merkkijonon, jossa joukkueet
    ovat aakkosjärjestyksessä rivinvaihdoilla erotettuna"""
    return "\n".join(sorted(map(lambda team: team['nimi'], teams), key=lambda name: name.lower()))


def add_team(series: dict, team: dict):
    """Lisää joukkueen sarjaan, arpoo joukkueelle uuden id:n jos id:tä ei ole"""
    if team['id'] == -1:
        team['id'] = generate_random_id(parse_teams(load_data(remote=False)))
    series['joukkueet'].append(team)

def remove_team(series: dict, team_name: str):
    print(team_name)
    teams = [team for team in series['joukkueet'] if team['nimi'] != team_name]
    series['joukkueet'] = teams

def generate_random_id(teams: list, iter: int=0):
    """Luo joukkueelle uniikin id:n"""

    # estetään ikuinen rekursio
    if iter > 10:
        return -1

    # arvotaan satunnainen id, yhteentörmäyksen sattuessa arvotaan uusi
    rdm = random.randint(1000000000000000,9999999999999999)
    if rdm in map(lambda team: team['id'], teams):
        rdm = generate_random_id(teams, iter + 1)

    return rdm

def calculate_points(team: dict, checkpoints: list):
    #TODO reduce

    print("parsing punches for: " + team['nimi'])
    parsed_punches = parse_punches(team['rastit'], checkpoints)

    print()
    print(f"{team['nimi']}: rastit:")
    print(parsed_punches)

    total = 0
    for punch in parsed_punches:
        total += get_points(punch[1])

    return total


def parse_punches(punches: list, checkpoints: list):
    # TODO generator expression
    punched_checkpoints = set()
    parsed_punches = []
    valid_punches = []

    for punch in punches:
        checkpoint = find_checkpoint_by_id(punch['rasti'], checkpoints)
        if checkpoint:
            parsed_punches.append((punch['aika'], checkpoint['koodi'], checkpoint['lat'], checkpoint['lon']))

    start_end_timestamps = _get_start_end_punches(parsed_punches)

    for punch in parsed_punches:
        if _is_valid_punch(punch, start_end_timestamps, punched_checkpoints):
            valid_punches.append(punch)

    return valid_punches

def _is_valid_punch(punch, start_end_punches: dict, punched_checkpoints: set):
    if punch[1] in punched_checkpoints:
        return False

    timestamp = datetime.fromisoformat(punch[0])
    start = start_end_punches['start'][1]
    end = start_end_punches['end'][1]

    print(f"{timestamp}, start={start}, end={end}")
    valid = start < timestamp < end
    if valid:
        punched_checkpoints.add(punch[1])

    return valid


def _get_start_end_punches(parsed_punches: list):
    start_datetime = None
    start_punch = None
    end_datetime = None
    end_punch = None

    for punch in parsed_punches:
        if punch[1] == 'LAHTO':
            start_timestamp = punch[0]
            temp_datetime = datetime.fromisoformat(start_timestamp) if start_timestamp else None
            if (not start_datetime or temp_datetime > start_datetime):
                start_datetime = temp_datetime
                start_punch = punch

    if start_datetime:
        for punch in parsed_punches:
            if punch[1] == 'MAALI':
                end_timestamp = punch[0]
                temp_datetime = datetime.fromisoformat(end_timestamp) if end_timestamp else None
                if (temp_datetime > start_datetime and (not end_datetime or temp_datetime < end_datetime)):
                    end_datetime = temp_datetime
                    end_punch = punch

    return {
        'start': (start_punch, start_datetime),
        'end': (end_punch, end_datetime)}

def print_teams(teams: list):
    """Muodostaa joukkueiden nimistä merkkijonon, jossa joukkueet
    ovat aakkosjärjestyksessä rivinvaihdoilla erotettuna"""

    rows = []
    for team in teams:
        rows.append(f"{team['name']}, points: {calculate_points(team)}")

    return rows