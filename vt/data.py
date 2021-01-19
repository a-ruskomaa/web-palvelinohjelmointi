#sama kuin simplejson mutta sisäänrakennettu moduli
import json
import os
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

