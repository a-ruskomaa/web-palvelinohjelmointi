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


######## SARJA ########

def hae_sarjat(kilpailu_id: int) -> Union[dict, None]:
    ancestor = {
        'kind': 'kilpailu',
        'id': kilpailu_id
    }
    res = db.hae_monta(kind='kilpailu', ancestor=ancestor)
    return res


def hae_sarjat_ja_joukkueet(kilpailu_id: int) -> Union[dict, None]:
    pass


######## JOUKKUE ########

def hae_joukkueet(sarja_id: int) -> Union[dict, None]:
    pass


def hae_joukkue(joukkue_id) -> Union[dict, None]:
    pass


def paivita_joukkue(joukkue: dict) -> int:
    pass


def lisaa_joukkue(joukkue: dict) -> int:
    pass


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

# nopeasti kyhättyjä apufunktioita, joilla saa muotoiltua tietokannasta haetun
# datan helpommin kásiteltävään muotoon

def _luo_sarja_dict(rivit):
    """ Luo monitasoisen hakemiston haetuista sarjoista.

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
    """ Luo hakemiston joukkueen tiedoista.
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