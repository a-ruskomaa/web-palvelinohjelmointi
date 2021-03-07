from sqlite3.dbapi2 import Row
import ast
from typing import Union
from . import db

# Moduli sisältää etukäteen muotoiltuja tietokantakutsuja. Valitettavasti en jaksanut näprätä näitä

######## KANTAKUTSUT ########


######## KILPAILU ########

def hae_kilpailu(kilpailu_id) -> Union[dict, None]:
    res = db.hae_yksi(kind='kilpailu', id=kilpailu_id)
    return res


def hae_kilpailut() -> Union[list, None]:
    res = db.hae_monta(kind='kilpailu')
    return res
    return _luo_dict_riveista(res)


######## SARJA ########


def hae_sarja(sarja_id) -> Union[dict, None]:
    res = db.hae_yksi(kind='sarja', id=sarja_id)
    return res


def hae_sarjat(kilpailu_id: int = None) -> Union[dict, None]:
    if kilpailu_id:
        ancestor = {
            'kind': 'kilpailu',
            'id': kilpailu_id
        }
        res = db.hae_monta(kind='sarja', ancestor=ancestor)
    else:
        res = db.hae_monta(kind='sarja')
    return res
    return _luo_dict_riveista(res)


######## JOUKKUE ########


def hae_joukkue(joukkue_id: int = None, params: dict = None) -> Union[dict, None]:
    return db.hae_yksi(kind='joukkue', id=joukkue_id, params=params)


def hae_joukkueet(sarja_id: int = None) -> Union[dict, None]:
    if sarja_id:
        ancestor = {
            'kind': 'sarja',
            'id': sarja_id
        }
        res = db.hae_monta(kind='joukkue', ancestor=ancestor)
    else:
        res = db.hae_monta(kind='joukkue')

    return res
    return _luo_dict_riveista(res)



def paivita_joukkue(joukkue: dict) -> int:
    res = db.kirjoita(kind='joukkue', obj=joukkue)
    return res


def lisaa_joukkue(joukkue: dict, parent_id: int) -> int:
    parent = {
        'kind': 'sarja',
        'id': parent_id
    }
    res = db.kirjoita(kind='joukkue', obj=joukkue, parent=parent)
    return res


def poista_joukkue(joukkue_id: int) -> int:
    pass


def hae_joukkue_nimella(kilpailu_id: int, joukkue_nimi: str) -> Union[dict, None]:
    pass



######## RASTI ########


def hae_kilpailun_rastit(kilpailu_id: int) -> Union[dict, None]:
    pass


def hae_kilpailun_rastit_ja_leimaukset(kilpailu_id: int) -> Union[dict, None]:
    pass


######## LEIMAUS ########


def hae_joukkueen_leimaukset(joukkue_id: int) -> Union[dict, None]:
    pass


def paivita_leimaus(joukkue_id: int, uusi_aika: str, uusi_rasti_id: int, vanha_aika: str, vanha_rasti_id: int) -> int:
    pass


def poista_leimaus(joukkue_id: int, aika: str, rasti_id: int) -> int:
    pass


######## APUFUNKTIOT ########

def _luo_dict_riveista(rivit):
    """ Muuntaa rivit automaattisesti pythonin hakemistoksi muodossa:

    {
        id1: {
            key1: value1,
            key2: value2,
            ...
        },
        id2: { ... }
    }
    """
    return {rivi.id:{key:rivi[key] for key in rivi.keys()} for rivi in rivit}


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