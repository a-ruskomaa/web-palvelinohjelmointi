import random
from vt.data.data import load_data


def create_team(name, members, id, punching_methods):
    return {
        "nimi": name,
        "jasenet": members,
        "id": id,
        "leimaustapa": punching_methods,
        "rastit": []
    }


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
    teams = [team for team in series['joukkueet'] if team['nimi'].lower() != team_name.lower()]
    series['joukkueet'] = teams

def update_team(data: dict, new_series: dict, updated_team: dict):
    """Päivittää argumenttina annetun joukkueen tiedot. Joukkue tunnistetaan id:n perusteella.
    Jos argumenttina annettu sarja eroaa aiemmasta sarjasta, siirretään joukkue uuteen sarjaan
    (jos tämä sarja on olemassa)"""
    old_series = None
    old_index = -1

    # Etsitään joukkuetta annetusta sarjasta
    for series in data['sarjat']:
        for index, team in enumerate(series['joukkueet']):
            if team['id'] == updated_team['id']:
                old_series = series
                old_index = index
                break
        if old_index != -1:
            break

    # Jos joukkuetta ei löytynyt
    if old_index == -1:
        return

    team = old_series['joukkueet'][old_index]

    # Korvataan joukkueen tiedot päivitetyillä tiedoilla
    team['nimi'] = updated_team['nimi']
    team['jasenet'] = updated_team['jasenet']
    team['leimaustapa'] = updated_team['leimaustapa']

    # Jos annettu sarja on olemassa, eikä ole sama kuin aiempi, vaihdetaan joukkueen sarjaa
    if new_series and (new_series['nimi'] != old_series['nimi']):
        old_series['joukkueet'].pop(old_index)
        new_series['joukkueet'].append(team)


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

