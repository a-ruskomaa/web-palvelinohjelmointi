#sama kuin simplejson mutta sisäänrakennettu moduli
import json
import os
import urllib.request

DATA_REMOTE_URL = "http://hazor.eu.pythonanywhere.com/2021/data.json"
DATA_PATH = os.path.join(os.getcwd(), 'data')
DATA_FILENAME = 'data.json'

def load_data(remote=False) -> dict:
    """Lataa json-muotoisen datan ja muuntaa sen pythonin dictionaryksi """
    if remote:
        # Ladataan data ulkoiselta palvelimelta
        data = _reset_data()
    else:
        with open(os.path.join(DATA_PATH, DATA_FILENAME), encoding="UTF-8", mode="r") as file:
                data = json.load(file)
    return data

def save_data(data):
    """Tallentaa datan tiedostoon"""
    try:
        os.makedirs(DATA_PATH)
    except OSError:
        pass

    with open(os.path.join(DATA_PATH, DATA_FILENAME), encoding="UTF-8", mode="w") as file:
        json.dump(data, file, ensure_ascii=False)


def _reset_data():
    """Lataa oletusdatan palvelimelta ja korvaa sillä paikallisen datan"""
    data = None
    with urllib.request.urlopen(DATA_REMOTE_URL) as response:
            data = json.load(response)
            # Korvataan paikallisesti tallennettu data palvelimen datalla
            save_data(data)
    return data