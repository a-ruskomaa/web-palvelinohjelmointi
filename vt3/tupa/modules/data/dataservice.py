from sqlite3.dbapi2 import Row
import ast
from . import db

# Moduli sisältää etukäteen muotoiltuja tietokantakutsuja. Valitettavasti en jaksanut näprätä näitä

######## KANTAKUTSUT ########

def hae_kilpailu(kilpailu_id) -> dict:
    sql = """SELECT nimi, id FROM kilpailut
            WHERE id = %s"""

    params = (kilpailu_id,)
    rivi = db.hae_yksi(sql, params)

    return dict(**rivi) if rivi else None


def hae_kilpailut() -> dict:
    sql = """SELECT nimi, id FROM kilpailut"""

    rivit = db.hae_monta(sql)
    
    return _luo_dict_riveista(rivit)


def hae_sarjat(kilpailu_id: int) -> dict:
    sql = """SELECT id AS sarja_id,
                    nimi AS sarja_nimi
            FROM sarjat
            WHERE sarjat.kilpailu = %s
            ORDER BY sarja_nimi ASC"""

    params = (kilpailu_id,)
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
    WHERE sarjat.kilpailu = %s
    ORDER BY
        sarja_nimi ASC,
        lower(joukkue_nimi) ASC"""

    params = (kilpailu_id,)

    rivit = db.hae_monta(sql, params)
    return _luo_sarja_dict(rivit)


def hae_joukkueet(sarja_id: int) -> dict:
    sql = """SELECT id AS joukkue_id,
                    nimi AS joukkue_nimi,
                    sarja AS joukkue_sarja,
                    salasana AS joukkue_salasana,
                    jasenet AS joukkue_jasenet
            FROM joukkueet
            WHERE joukkueet.sarja = %s
            ORDER BY lower(joukkue_nimi) ASC"""

    params = (sarja_id,)
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
            WHERE joukkueet.id = %s"""

    params = (joukkue_id,)
    rivi = db.hae_yksi(sql, params)
    return _luo_joukkue_dict(rivi)



def paivita_joukkue(joukkue: dict):
    sql = """UPDATE joukkueet SET
            nimi = %s,
            salasana = %s,
            sarja = %s,
            jasenet = %s
            WHERE id = %s"""

    params = (joukkue['nimi'], joukkue['salasana'], joukkue['sarja'], joukkue['jasenet'], joukkue['id'])
    db.kirjoita(sql, params)


def lisaa_joukkue(joukkue: dict):
    sql = """INSERT INTO joukkueet
            (nimi, sarja, jasenet) VALUES
            (%s, %s, %s)"""

    params = (joukkue['nimi'], joukkue['sarja'], joukkue['jasenet'])
    return db.kirjoita(sql, params)


def poista_joukkue(joukkue_id: int):
    sql = """DELETE FROM joukkueet
            WHERE joukkueet.id = %s"""
    
    params = (joukkue_id,)
    return db.kirjoita(sql, params)



def hae_joukkue_nimella(kilpailu_id: int, joukkue_nimi: str) -> dict:
    sql = """SELECT joukkueet.id AS id,
                    joukkueet.nimi AS nimi,
                    joukkueet.salasana AS salasana,
                    joukkueet.sarja AS sarja,
                    joukkueet.jasenet AS jasenet
            FROM joukkueet
            JOIN sarjat ON joukkueet.sarja = sarjat.id
            JOIN kilpailut ON sarjat.kilpailu = kilpailut.id
            WHERE sarjat.kilpailu = %s
            AND trim(upper(joukkueet.nimi))
            = trim(upper(%s))"""
            
    params = (kilpailu_id, joukkue_nimi)

    rivi = db.hae_yksi(sql, params)
    return dict(**rivi) if rivi else None


def hae_kilpailun_rastit(kilpailu_id: int):
    sql = """SELECT id, koodi, lat, lon FROM rastit
            WHERE rastit.kilpailu = %s"""

    params = (kilpailu_id,)

    rivit = db.hae_monta(sql, params)
    return _luo_taulukko_riveista(rivit)


def hae_kilpailun_rastit_ja_leimaukset(kilpailu_id: int):
    sql = """SELECT id, koodi, lat, lon, Count(tupa.aika) AS leimauksia FROM rastit
            LEFT JOIN tupa ON
            tupa.rasti = rastit.id
            WHERE rastit.kilpailu = %s
            GROUP BY rastit.id
            ORDER BY rastit.koodi DESC"""

    params = (kilpailu_id,)

    rivit = db.hae_monta(sql, params)
    return _luo_taulukko_riveista(rivit)


def hae_joukkueen_leimaukset(joukkue_id: int):
    sql = """SELECT aika, rasti, koodi, joukkue FROM tupa
            JOIN rastit ON
            tupa.rasti = rastit.id
            WHERE joukkue = %s"""
    
    params = (joukkue_id,)

    rivit = db.hae_monta(sql, params)
    return _luo_taulukko_riveista(rivit)


def paivita_leimaus(joukkue_id: int, uusi_aika: str, uusi_rasti_id: int, vanha_aika: str, vanha_rasti_id: int):
    sql = """UPDATE tupa SET
            aika = %s,
            rasti = %s
            WHERE joukkue = %s
            AND aika = %s
            AND rasti = %s"""

    params = (uusi_aika, uusi_rasti_id, joukkue_id, vanha_aika, vanha_rasti_id)

    return db.kirjoita(sql, params)


def poista_leimaus(joukkue_id: int, aika: str, rasti_id: int):
    sql = """DELETE FROM tupa
            WHERE joukkue = %s
            AND aika = %s
            AND rasti = %s"""

    params = (joukkue_id, aika, rasti_id)

    return db.kirjoita(sql, params)


######## APUFUNKTIOT ########

# nopeasti kyhättyjä apufunktioita, joilla saa muotoiltua tietokannasta haetun
# datan helpommin kásiteltävään muotoon

def _luo_sarja_dict(rivit):
    """ Luo monitasoisen dictionaryn haetuista sarjoista.

    Jos annetut rivit sisältävät myös joukkueiden tiedot, lisätään
    joukkueet mukaan palautettavaan tietorakenteeseen.

    Palautettu muoto:
    {
        sarja1_id: {
            id: id.
            nimi: nimi,
            joukkueet: {
                joukkue1_id: { ... },
                joukkue2_id: { ... }
            }
        },
        sarja2_id: {
             ...
        }
    }
    """
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
    """ Luo dictionaryn joukkueen tiedoista.
    Salasanaa tai sarjaa ei ole pakko olla annetussa rivissä. """

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


def _luo_dict_riveista(rivit):
    """ Muuntaa rivit automaattisesti pythonin dictionaryksi muodossa:
    {
        id1: {
            key1: value1,
            key2: value2,
            ...
        },
        id2: { ... }
    }
    """
    return {rivi['id']:{key:rivi[key] for key in rivi.keys()} for rivi in rivit}


def _luo_taulukko_riveista(rivit):
    """ Muuntaa rivit automaattisesti taulukoksi hakemistoja muodossa:
    [{
        key1: value1,
        key2: value2,
        ...
    },
    {
        ...
    }]
    """
    return [{key:rivi[key] for key in rivi.keys()} for rivi in rivit]