#sama kuin simplejson mutta sisäänrakennettu moduli
import json
import os
import random
import urllib.request

# def hello(name):
#     return f"Hello {name}"

DATA_LOCATION = "http://hazor.eu.pythonanywhere.com/2021/data.json"

def download_data(location=DATA_LOCATION) -> dict:
    """Lataa json-muotoisen datan ja muuntaa sen pythonin dictionaryksi """
    with urllib.request.urlopen(location) as response:
        data = json.load(response)
        return data


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
    series['joukkueet'].append(team)


def find_max_id(teams: list):
    return max(map(lambda team: team['id'], teams))


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