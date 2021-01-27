import random
from vt.data.data import load_data

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
        team['id'] = _generate_random_id(parse_teams(load_data(remote=False)))
    series['joukkueet'].append(team)


def remove_team(series: dict, team_name: str):
    """Poistaa joukkueen sarjasta"""
    teams = [team for team in series['joukkueet'] if team['nimi'] != team_name]
    series['joukkueet'] = teams

def update_team(series: dict, team_name: str):
    pass


def _generate_random_id(teams: list, iter: int=0):
    """Luo joukkueelle uniikin id:n"""

    # estetään ikuinen rekursio
    if iter > 10:
        return -1

    # arvotaan satunnainen id, yhteentörmäyksen sattuessa arvotaan uusi
    rdm = random.randint(1000000000000000,9999999999999999)
    if rdm in (team['id'] for team in teams):
        rdm = _generate_random_id(teams, iter + 1)

    return rdm

