#sama kuin simplejson mutta sisäänrakennettu moduli
import json
import os
import random
import urllib.request

DATA_REMOTE_URL = "http://hazor.eu.pythonanywhere.com/2021/data.json"
DATA_FILENAME = "data.json"

def load_data(local=False) -> dict:
    """Lataa json-muotoisen datan ja muuntaa sen pythonin dictionaryksi """
    if local:
        with open(DATA_FILENAME, encoding="UTF-8", mode="r") as file:
            data = json.load(file)
    else:
        data = reset_data()

    return data

def reset_data():
    with urllib.request.urlopen(DATA_REMOTE_URL) as response:
        data = json.load(response)

    with open(DATA_FILENAME, encoding="UTF-8", mode="w") as file:
        json.dump(data, file, ensure_ascii=False)

    return data

def parse_teams(data: dict):
    """Parsii datasta kaikki joukkueet tiedot ja palauttaa ne listalla"""
    teams = []

    for sarja in data['sarjat']:
        for joukkue in sarja['joukkueet']:
            teams.append(joukkue)

    return teams


def get_series_by_name(name: str):
    data = load_data(local=True)


def names_to_string(teams: list):
    """Muodostaa joukkueiden nimistä merkkijonon, jossa joukkueet
    ovat aakkosjärjestyksessä rivinvaihdoilla erotettuna"""
    return "\n".join(sorted(map(lambda team: team['nimi'], teams), key=lambda name: name.lower()))


def checkpoints_to_string(checkpoints: list):
    """Palauttaa kaikki kokonaisluvulla alkavat rastikoodit yhtenä merkkijonona"""
    def filter_checkpoints(checkpoint) -> bool:
        """Suodatetaan rasteista pois rastit joiden koodin ensimmäinen merkki ei ole numero"""
        try:
            int(checkpoint['koodi'][0])
            return True
        except ValueError:
            return False
        
    return ";".join(map(lambda cp: cp['koodi'], filter(filter_checkpoints, checkpoints)))


def add_team(series: dict, team: dict):
    """Lisää joukkueen sarjaan, arpoo joukkueelle uuden id:n jos id:tä ei ole"""
    print(team)
    if team['id'] == -1:
        team['id'] = generate_random_id(parse_teams(load_data(local=True)))
    print(team)
    series['joukkueet'].append(team)


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