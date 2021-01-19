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
    teams = []

    for sarja in data['sarjat']:
        for joukkue in sarja['joukkueet']:
            teams.append(joukkue)

    return teams