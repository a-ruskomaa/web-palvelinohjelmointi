from sqlite3.dbapi2 import Row
import ast
from . import db


######## KANTAKUTSUT ########


def hae_kilpailut() -> dict:
    sql = """SELECT nimi, id FROM kilpailut"""

    rivit = db.hae_monta(sql)
    
    kilpailut = {rivi['id']:{key:rivi[key] for key in rivi.keys()} for rivi in rivit}

    return kilpailut


def hae_sarjat(kilpailu_id: int) -> dict:
    sql = """SELECT id AS sarja_id,
                    nimi AS sarja_nimi
            FROM sarjat
            WHERE sarjat.kilpailu = :kilpailu_id
            ORDER BY sarja_nimi ASC"""

    params = {'kilpailu_id': kilpailu_id}
    rivit = db.hae_monta(sql, params)
    return _luo_sarja_dict(rivit)


def hae_sarjat_ja_joukkueet(kilpailu_id: int) -> dict:
    sql = """
    SELECT sarjat.id AS sarja_id,
           sarjat.nimi AS sarja_nimi,
           joukkueet.id AS joukkue_id,
           joukkueet.nimi AS joukkue_nimi,
           joukkueet.jasenet AS joukkue_jasenet
    FROM joukkueet
    JOIN sarjat ON joukkueet.sarja = sarjat.id
    JOIN kilpailut ON sarjat.kilpailu = kilpailut.id
    WHERE sarjat.kilpailu = :kilpailu_id
    ORDER BY
        sarja_nimi ASC,
        lower(joukkue_nimi) ASC"""

    params = {'kilpailu_id': kilpailu_id}

    rivit = db.hae_monta(sql, params)
    return _luo_sarja_dict(rivit)


def hae_joukkueet(sarja_id: int) -> dict:
    sql = """SELECT id AS joukkue_id,
                    nimi AS joukkue_nimi,
                    sarja AS joukkue_sarja,
                    salasana AS joukkue_salasana,
                    jasenet AS joukkue_jasenet
            FROM joukkueet
            WHERE joukkueet.sarja = :sarja_id
            ORDER BY lower(joukkue_nimi) ASC"""

    params = {'sarja_id': sarja_id}
    rivit = db.hae_monta(sql, params)

    joukkueet = {rivi['joukkue_id']:_luo_joukkue_dict(rivi) for rivi in rivit}

    return joukkueet


def hae_joukkue(joukkue_id):
    sql = """SELECT id AS joukkue_id,
                    nimi AS joukkue_nimi,
                    sarja AS joukkue_sarja,
                    salasana AS joukkue_salasana,
                    jasenet AS joukkue_jasenet
            FROM joukkueet
            WHERE joukkueet.id = :joukkue_id"""

    params = {'joukkue_id': joukkue_id}
    rivi = db.hae_yksi(sql, params)
    return _luo_joukkue_dict(rivi)


def tallenna_joukkue(joukkue: dict):
    sql = """UPDATE joukkueet SET
            nimi = :nimi,
            sarja = :sarja,
            jasenet = :jasenet
            WHERE id = :id"""

    params = joukkue
    db.lisaa(sql, params)


def hae_joukkue_nimella(kilpailu_id: int, joukkue_nimi: str) -> dict:
    sql = """SELECT joukkueet.id AS id,
                    joukkueet.nimi AS nimi,
                    joukkueet.salasana AS salasana,
                    joukkueet.sarja AS sarja,
                    joukkueet.jasenet AS jasenet
            FROM joukkueet
            JOIN sarjat ON joukkueet.sarja = sarjat.id
            JOIN kilpailut ON sarjat.kilpailu = kilpailut.id
            WHERE sarjat.kilpailu = :kilpailu_id
            AND trim(upper(joukkueet.nimi))
            = trim(upper(:joukkue_nimi))"""
            
    params = {'kilpailu_id': kilpailu_id,
              'joukkue_nimi': joukkue_nimi}

    rivi = db.hae_yksi(sql, params)
    return dict(**rivi) if rivi else None


######## HELPERS ########


def _luo_sarja_dict(rivit):
    sarjat = {}
    for rivi in rivit:
        sarja_id = rivi['sarja_id']
        if not sarjat.get(sarja_id):
            sarja_nimi = rivi['sarja_nimi']
            sarjat[sarja_id] = {
                'id': sarja_id,
                'nimi': sarja_nimi,
                'joukkueet': {}}
        
        try:
            joukkue_id = rivi['joukkue_id']
            sarjat[sarja_id]['joukkueet'][joukkue_id] = _luo_joukkue_dict(rivi)
        except (KeyError, IndexError):
            continue

    return sarjat


def _luo_joukkue_dict(rivi: Row):
    joukkue_id = rivi['joukkue_id']
    joukkue_nimi = rivi['joukkue_nimi']
    joukkue_jasenet = rivi['joukkue_jasenet']
    joukkue_sarja = rivi['joukkue_sarja'] if 'joukkue_sarja' in rivi.keys() else None
    joukkue_salasana = rivi['joukkue_salasana'] if 'joukkue_salasana' in rivi.keys() else None
    
    return {
                'id': joukkue_id,
                'nimi': joukkue_nimi,
                'jasenet': ast.literal_eval(joukkue_jasenet),
                'sarja': joukkue_sarja,
                'salasana': joukkue_salasana
            }


