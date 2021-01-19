def get_series_by_name(name: str, data: dict):
    """Palauttaa parametrina annettua nimeä vastaavan sarjan dictionaryna"""
    for sarja in data['sarjat']:
        if sarja['nimi'] == name:
            return sarja

    return None