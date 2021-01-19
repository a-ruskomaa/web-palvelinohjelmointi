#sama kuin simplejson mutta sisäänrakennettu moduli
import json
import os
import urllib.request

DATA_REMOTE_URL = "http://hazor.eu.pythonanywhere.com/2021/data.json"
DATA_FILENAME = "data.json"

def load_data(local=False) -> dict:
    """Lataa json-muotoisen datan ja muuntaa sen pythonin dictionaryksi """
    if local:
        with open(DATA_FILENAME, encoding="UTF-8", mode="r") as file:
            data = json.load(file)
    else:
        data = _reset_data()

    return data

def save_data(data):
    with open(DATA_FILENAME, encoding="UTF-8", mode="w") as file:
        json.dump(data, file, ensure_ascii=False)


def _reset_data():
    """Lataa oletusdatan palvelimelta ja korvaa sillä paikallisen datan"""
    # TODO virheenkäsittely 
    with urllib.request.urlopen(DATA_REMOTE_URL) as response:
        data = json.load(response)
        save_data(data)

    return data