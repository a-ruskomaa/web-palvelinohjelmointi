from sqlite3.dbapi2 import Row
import ast
from typing import List, Union

from google.cloud.datastore.entity import Entity
from . import db

# Moduli sisältää etukäteen muotoiltuja tietokantakutsuja. Valitettavasti en jaksanut näprätä näitä

######## KANTAKUTSUT ########


######## KILPAILU ########

def hae_kilpailu(kilpailu_id) -> Union[Entity, None]:
    print("Haetaan kilpailu")
    if not kilpailu_id:
        return None
    res = db.hae_yksi(kind='kilpailu', id=kilpailu_id)
    return res


def hae_kilpailut() -> Union[List[Entity], None]:
    res = db.hae_monta(kind='kilpailu')
    return res


######## SARJA ########


def hae_sarja(sarja_id, kilpailu_id) -> Union[Entity, None]:
    ancestors = None
    print("Haetaan sarja")
    if not (sarja_id and kilpailu_id):
        return None
    ancestors = {
        'kilpailu': kilpailu_id
    }
    res = db.hae_yksi(kind='sarja', id=sarja_id, ancestors=ancestors)
    return res


def hae_sarjat(kilpailu_id: int = None) -> Union[dict, None]:
    ancestors = None
    
    if kilpailu_id:
        ancestors = {
            'kilpailu': kilpailu_id
        }
    
    res = db.hae_monta(kind='sarja', ancestors=ancestors)

    return res


######## JOUKKUE ########


def hae_joukkue(joukkue_id: int = None, sarja_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[Entity, None]:
    ancestors = None
    print("Haetaan joukkue")
    if not (joukkue_id or filters):
        # TODO heitä poikkeus?
        return None
    if sarja_id and kilpailu_id:
        ancestors = {
            'kilpailu': kilpailu_id,
            'sarja': sarja_id
        }
    return db.hae_yksi(kind='joukkue', id=joukkue_id, ancestors=ancestors, filters=filters)


def hae_joukkueet(sarja_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[dict, None]:
    ancestors = None
    if kilpailu_id:
        ancestors = {
            'kilpailu': kilpailu_id
        }
        if sarja_id:
            ancestors.update({'sarja': sarja_id})

    res = db.hae_monta(kind='joukkue', ancestors=ancestors, filters=filters)

    return res



def paivita_joukkue(joukkue: dict, joukkue_id: int, sarja_id: int, kilpailu_id: int) -> int:
    ancestors = {
        'kilpailu': kilpailu_id,
        'sarja': sarja_id
    }
    res = db.kirjoita(kind='joukkue', id=joukkue_id, obj=joukkue, ancestors=ancestors)
    return res


def lisaa_joukkue(joukkue: dict, sarja_id: int, kilpailu_id: int) -> int:
    ancestors = {
        'kilpailu': kilpailu_id,
        'sarja': sarja_id
    }
    res = db.kirjoita(kind='joukkue', obj=joukkue, ancestors=ancestors)
    return res


def poista_joukkue(joukkue_id: int, sarja_id: int, kilpailu_id: int) -> int:

    ancestors = {
        'kilpailu': kilpailu_id,
        'sarja': sarja_id
    }
    
    db.poista(kind='joukkue', id=joukkue_id, ancestors=ancestors)
    pass


def hae_joukkue_nimella(kilpailu_id: int, joukkue_nimi: str) -> Union[Entity, None]:
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