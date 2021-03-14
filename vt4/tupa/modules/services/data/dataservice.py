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

        return self.db.hae_yksi(kind='kilpailu', id=kilpailu_id)


    def hae_kilpailut(self) -> Union[List[Entity], None]:
        return self.db.hae_monta(kind='kilpailu', order=['nimi'])


    ######## SARJA ########


    def hae_sarja(self, sarja_id, kilpailu_id) -> Union[Entity, None]:
        if not (sarja_id and kilpailu_id):
            return None

        ancestors = None

        ancestors = {
            'kilpailu': kilpailu_id
        }
        return self.db.hae_yksi(kind='sarja', id=sarja_id, ancestors=ancestors)


    def hae_sarjat(self, kilpailu_id: int = None) -> Union[dict, None]:
        ancestors = None

        if kilpailu_id:
            ancestors = {
                'kilpailu': kilpailu_id
            }
        return self.db.hae_monta(kind='sarja', ancestors=ancestors, order=['nimi'])


    ######## JOUKKUE ########


    def hae_joukkue(self, joukkue_id: int = None, sarja_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[Entity, None]:
        if not (joukkue_id or filters):
            return None

        ancestors = None

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

        return self.db.hae_monta(kind='joukkue', ancestors=ancestors, filters=filters, order=['nimi'])


    def lisaa_joukkue(self, joukkue: dict, sarja_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'sarja': sarja_id
        }
        return self.db.kirjoita(kind='joukkue', obj=joukkue, ancestors=ancestors)


    def paivita_joukkue(self, joukkue: dict, joukkue_id: int, sarja_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'sarja': sarja_id
        }
        return self.db.kirjoita(kind='joukkue', id=joukkue_id, obj=joukkue, ancestors=ancestors)



    def poista_joukkue(self, joukkue_id: int, sarja_id: int, kilpailu_id: int) -> None:
        ancestors = {
            'kilpailu': kilpailu_id,
            'sarja': sarja_id
        }
        self.db.poista(kind='joukkue', id=joukkue_id, ancestors=ancestors)


    ######## RASTI ########


    def hae_rasti(self, rasti_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[Entity, None]:
        if not (rasti_id or filters):
            return None

        ancestors = None

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
        return self.db.hae_monta(kind='rasti', ancestors=ancestors, filters=filters, order=['-koodi'])


    def lisaa_rasti(self, rasti: dict, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id
        }
        return self.db.kirjoita(kind='rasti', obj=rasti, ancestors=ancestors)

    
    def paivita_rasti(self, rasti: dict, rasti_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id
        }
        return self.db.kirjoita(kind='rasti', id=rasti_id, obj=rasti, ancestors=ancestors)


    def poista_rasti(self, rasti_id: int, kilpailu_id: int) -> None:
        ancestors = {
            'kilpailu': kilpailu_id
        }
        self.db.poista(kind='rasti', id=rasti_id, ancestors=ancestors)
    

    ######## LEIMAUS ########


    def hae_leimaus(self, leimaus_id: int = None, joukkue_id: int = None, kilpailu_id: int = None, filters: dict = None) -> Union[dict, None]:

        if not (leimaus_id or filters):
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
        
        return self.db.hae_monta(kind='leimaus', ancestors=ancestors, filters=filters, order=['aika'])


    def lisaa_leimaus(self, leimaus: dict, joukkue_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'joukkue': joukkue_id
        }
        return self.db.kirjoita(kind='leimaus', obj=leimaus, ancestors=ancestors)


    def paivita_leimaus(self, leimaus: dict, leimaus_id: int, joukkue_id: int, kilpailu_id: int) -> int:
        ancestors = {
            'kilpailu': kilpailu_id,
            'joukkue': joukkue_id
        }
        return self.db.kirjoita(kind='leimaus', id=leimaus_id, obj=leimaus, ancestors=ancestors)


    def poista_leimaus(self, leimaus_id: int, joukkue_id: int, kilpailu_id: int) -> None:
        ancestors = {
            'kilpailu': kilpailu_id,
            'joukkue': joukkue_id
        }
        self.db.poista(kind='rasti', id=leimaus_id, ancestors=ancestors)
