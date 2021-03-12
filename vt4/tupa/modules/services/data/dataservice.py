from tupa.modules.services.data.database import Database
from typing import List, Union
from google.cloud.datastore.entity import Entity

class DataService():

    def __init__(self, db: Database):
        self.db = db

    ######## KILPAILU ########

    def hae_kilpailu(self, kilpailu_id) -> Union[Entity, None]:
        if not kilpailu_id:
            return None
        res = self.db.hae_yksi(kind='kilpailu', id=kilpailu_id)
        return res


    def hae_kilpailut(self) -> Union[List[Entity], None]:
        res = self.db.hae_monta(kind='kilpailu')
        return res


    ######## SARJA ########


    def hae_sarja(self, sarja_id, kilpailu_id) -> Union[Entity, None]:
        ancestors = None
        if not (sarja_id and kilpailu_id):
            return None
        ancestors = {
            'kilpailu': kilpailu_id
        }
        res = self.db.hae_yksi(kind='sarja', id=sarja_id, ancestors=ancestors)
        return res


    def hae_sarjat(self, kilpailu_id: int = None) -> Union[dict, None]:
        ancestors = None
        
        if kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id
            }
        
        res = self.db.hae_monta(kind='sarja', ancestors=ancestors)

        return res


    ######## JOUKKUE ########


    def hae_joukkue(self, joukkue_id: int = None, sarja_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[Entity, None]:
        ancestors = None
        if not (joukkue_id or filters):
            # TODO heitä poikkeus?
            return None
        if sarja_id and kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id,
                'sarja': sarja_id
            }
        return self.db.hae_yksi(kind='joukkue', id=joukkue_id, ancestors=ancestors, filters=filters)


    def hae_joukkueet(self, sarja_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[dict, None]:
        ancestors = None
        if kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id
            }
            if sarja_id:
                ancestors.update({'sarja': sarja_id})

        res = self.db.hae_monta(kind='joukkue', ancestors=ancestors, filters=filters)

        return res


    def lisaa_joukkue(self, joukkue: dict, sarja_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'sarja': sarja_id
        }
        res = self.db.kirjoita(kind='joukkue', obj=joukkue, ancestors=ancestors)
        return res


    def paivita_joukkue(self, joukkue: dict, joukkue_id: int, sarja_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'sarja': sarja_id
        }
        res = self.db.kirjoita(kind='joukkue', id=joukkue_id, obj=joukkue, ancestors=ancestors)
        return res



    def poista_joukkue(self, joukkue_id: int, sarja_id: int, kilpailu_id: int) -> int:

        ancestors = {
            'kilpailu': kilpailu_id,
            'sarja': sarja_id
        }

        self.db.poista(kind='joukkue', id=joukkue_id, ancestors=ancestors)
        pass


    ######## RASTI ########


    def hae_rasti(self, rasti_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[Entity, None]:
        ancestors = None
        if not (rasti_id or filters):
            # TODO heitä poikkeus?
            return None
        if kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id
            }
        return self.db.hae_yksi(kind='rasti', id=rasti_id, ancestors=ancestors, filters=filters)


    def hae_rastit(self, kilpailu_id: int = None, filters: dict = None) -> Union[dict, None]:
        ancestors = None
        
        if kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id
            }
        
        res = self.db.hae_monta(kind='rasti', ancestors=ancestors, filters=filters)

        return res


    def lisaa_rasti(self, rasti: dict, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id
        }
        res = self.db.kirjoita(kind='rasti', obj=rasti, ancestors=ancestors)
        return res

    
    def paivita_rasti(self, rasti: dict, rasti_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id
        }
        res = self.db.kirjoita(kind='rasti', id=rasti_id, obj=rasti, ancestors=ancestors)
        return res


    def poista_rasti(self, rasti_id: int, kilpailu_id: int) -> int:

        ancestors = {
            'kilpailu': kilpailu_id
        }

        self.db.poista(kind='rasti', id=rasti_id, ancestors=ancestors)
    

    ######## LEIMAUS ########


    def hae_leimaus(self, leimaus_id: int = None, joukkue_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[dict, None]:
        ancestors = None
        if not (leimaus_id or filters):
            # TODO heitä poikkeus?
            return None
        ancestors = None
        if kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id
            }
            if joukkue_id:
                ancestors.update({'joukkue': joukkue_id})

        return self.db.hae_yksi(kind='leimaus', id=leimaus_id, ancestors=ancestors, filters=filters)


    def hae_leimaukset(self, joukkue_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[dict, None]:
        ancestors = None
        
        if kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id
            }
            if joukkue_id:
                ancestors.update({'joukkue': joukkue_id})
        
        res = self.db.hae_monta(kind='leimaus', ancestors=ancestors, filters=filters)

        return res


    def lisaa_leimaus(self, leimaus: dict, joukkue_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'joukkue': joukkue_id
        }
        res = self.db.kirjoita(kind='leimaus', obj=leimaus, ancestors=ancestors)
        return res


    def paivita_leimaus(self, leimaus: dict, leimaus_id: int, joukkue_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'joukkue': joukkue_id
        }
        res = self.db.kirjoita(kind='leimaus', id=leimaus_id, obj=leimaus, ancestors=ancestors)
        return res



    def poista_leimaus(self, leimaus_id: int, joukkue_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'joukkue': joukkue_id
        }

        self.db.poista(kind='rasti', id=leimaus_id, ancestors=ancestors)


    ######## APUFUNKTIOT ########

    def _luo_dict_riveista(self, rivit):
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


    def _luo_taulukko_riveista(self, rivit):
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