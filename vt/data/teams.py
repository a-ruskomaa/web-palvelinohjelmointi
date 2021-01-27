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
    return "\n".join(sorted((team['nimi'] for team in teams), key=lambda name: name.lower()))


def add_team(series: dict, team: dict):
    """Lisää joukkueen sarjaan, arpoo joukkueelle uuden id:n jos id:tä ei ole"""
    if team['id'] == -1:
        team['id'] = generate_random_id(parse_teams(load_data(remote=False)))
    series['joukkueet'].append(team)


def remove_team(series: dict, team_name: str):
    """Poistaa joukkueen sarjasta"""
    teams = [team for team in series['joukkueet'] if team['nimi'] != team_name]
    series['joukkueet'] = teams


def generate_random_id(teams: list, iter: int=0):
    """Luo joukkueelle uniikin id:n"""

    # estetään ikuinen rekursio
    if iter > 10:
        return -1

    # arvotaan satunnainen id, yhteentörmäyksen sattuessa arvotaan uusi
    rdm = random.randint(1000000000000000,9999999999999999)
    if rdm in (team['id'] for team in teams):
        rdm = generate_random_id(teams, iter + 1)

    return rdm

def calculate_statistics(team: dict, checkpoints: list):

    punches = team['rastit']

    # seulotaan rastileimauksista vain kelvolliset leimaukset
    valid_punches, start_punch, end_punch = parse_punches(punches, checkpoints)

    points = calculate_points(valid_punches)
    time = calculate_time(valid_punches)
    distance = calculate_total_distance(valid_punches)

    return points, time, distance



def calculate_time(valid_punches: list):
    return None


def calculate_total_distance(valid_punches: list):
    return None


def calculate_points(valid_punches: list):
    """Laskee pisteet annetuista rastileimauksista"""

    total = 0
    for punch in valid_punches:
        total += get_points(punch['rasti']['koodi'])

    return total



def parse_punches(punches: list, checkpoints: list):
    """Seuloo rastileimauksista vain kelvolliset leimaukset. Leimatun rastin id:n
    on vastattava todellista rastia ja leimauksen ajankohdan tulee olla lähtö- ja maalileimauksen
    välissä.
    
    Palauttaa tuplen muodossa: [(aika, koodi, lat, lon)], 
    """

    punched_checkpoints = set()
    parsed_punches = []
    valid_punches = []

    # Muunnetaan rastileimaukset muotoon {aika, {id, lat, lon, koodi}} ja karsitaan pois epäkelvot leimaukset
    for punch in punches:
        checkpoint = find_checkpoint_by_id(punch['rasti'], checkpoints)
        if checkpoint:
            parsed_punches.append({'aika': punch['aika'], 'rasti':checkpoint})

    start_punch, end_punch = _get_start_end_punches(parsed_punches)

    # Karsitaan toisella iteraatiolla leimaukset, jotka ovat sallitun aikavälin ulkopuolella
    # tai leimattu useammin kuin kerran
    for punch in parsed_punches:
        if _is_valid_punch(punch, start_punch, end_punch, punched_checkpoints):
            valid_punches.append(punch)

    return valid_punches, start_punch, end_punch


def _get_start_end_punches(parsed_punches: list):
    """Etsii myöhäisimmän lähtöleimauksen ja ensimmäisen maalileimauksen.
    
    Palauttaa dictionaryn muodossa {start: (lähtöleimaus, ajankohta), end: (maalileimaus, ajankohta)}"""
    start_datetime = None
    start_punch = None
    end_datetime = None
    end_punch = None

    # Etsitään ensimmäisellä iteraatiolla myöhäisin lähtöleimaus
    for punch in parsed_punches:
        if punch['rasti']['koodi'] == 'LAHTO':
            start_timestamp = punch['aika']
            temp_datetime = datetime.fromisoformat(start_timestamp) if start_timestamp else None

            # Hyväksytään ensimmäinen vastaantuleva lähtöleimaus sekä leimaus jonka
            # ajankohta on myöhemmin kuin aiemmin löydetty lähtöleimaus
            if (not start_datetime or temp_datetime > start_datetime):
                start_datetime = temp_datetime
                start_punch = punch

    # Etsitään toisella iteraatiolla ensimmäinen maalileimaus (vain jos lähtöleimaus löytyi)
    if start_datetime:
        for punch in parsed_punches:
            if punch['rasti']['koodi'] == 'MAALI':
                end_timestamp = punch['aika']
                temp_datetime = datetime.fromisoformat(end_timestamp) if end_timestamp else None

                # Hyväksytään ensimmäinen vastaantuleva maalileimaus sekä leimaus jonka
                # leimauksen ajankohta on myöhemmin kuin aiemmin löydetty lähtöleimaus.
                # Leimauksen tulee olla lähtöleimauksen jälkeen.
                if (temp_datetime > start_datetime and (not end_datetime or temp_datetime < end_datetime)):
                    end_datetime = temp_datetime
                    end_punch = punch

    return (start_punch, end_punch)


def _is_valid_punch(punch, start_punch, end_punch, punched_checkpoints: set):
    """Tarkistaa onko rastileimauksen aikaleima lähtö- ja maalileimauksen välissä ja
    onko rasti leimattu vain yhden kerran"""

    # Jos rasti on jo leimattu, ei kelpuuteta toista leimausta
    if punch['rasti']['koodi'] in punched_checkpoints:
        return False

    timestamp = datetime.fromisoformat(punch['aika'])
    start_timestamp = datetime.fromisoformat(start_punch['aika'])
    end_timestamp = datetime.fromisoformat(end_punch['aika'])

    # Kelpuutetaan leimaus vain jos se on sallitulla aikavälillä
    valid = start_timestamp < timestamp < end_timestamp
    if valid:
        # Lisätään kelvollisten leimausten joukkoon
        punched_checkpoints.add(punch['rasti']['koodi'])

    return valid
