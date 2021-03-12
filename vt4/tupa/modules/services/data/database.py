import json
import os
import requests
from datetime import datetime
from typing import List, Union
from flask import g
from google.cloud.datastore.client import Client
from google.cloud.datastore.entity import Entity

class Database:
    """ Tietokantatoteutuksen piilottava luokka.
    
    Luokka on alustettava flask-sovelluksen luomisen jälkeen kutsumalla
    metodia init_app().
    
    HUOM! Yksinkertaisuuden vuoksi ei sisällä poikkeuskäsittelyä tilanteissa
    joissa tietokantakutsu ei onnistu."""

    def __init__(self, app = None) -> None:
        self.app = app

        if app is not None:
            self.init_app(app)
    

    def init_app(self, app):
        """ Alustaa tietokannan. Valitsee käytetyn
        tietokantajärjestelmän suoritusympäsistön mukaan."""

        # tietokantayhteys katkaistaan automaattisesti käsitellyn HTTP-pyynnön jälkeen
        app.teardown_appcontext(self.sulje_yhteys)

        # valitaan tietokanta suoritusympäristön perusteella
        if app.env == 'development':
            self.db = DevDatastore(app)
        else:
            self.db = ProdDatastore(app)


    def avaa_yhteys(self) -> Client:
        """ Avaa tietokantayhteyden. Saman pyynnön aikana
        suoritetut tietokantakutsut suoritetaan samaa
        yhteyttä hyödyntäen. """

        # ensimmäinen tietokantakutsu avaa uuden yhteyden
        if 'db_conn' not in g:
            g.db_conn = self.db.avaa_yhteys()

        # palautetaan yhteys asiakkaan käyttöön
        return g.db_conn


    def sulje_yhteys(self, e=None):
        """ Sulkee tietokantayhteyden. Yhteys
        suljetaan automaattisesti pyynnön kontekstin
        purun aikana, joten yhteyden sulkeminen käsin
        on tarpeen vain poikkeustilanteissa. """

        db_conn = g.pop('db_conn', None)

        # if db_conn is not None:
        #     db_conn.close()


    def hae_yksi(self, kind: str, id: int = None, ancestors: dict = None, filters: dict = None) -> Entity:
        """ Suorittaa tietokantaan yhden rivin palauttavan haun. """

        client = self.avaa_yhteys()
        if id:
            print(f"Haetaan {kind} id:lla: {id}")
            key = self._rakenna_avain(client, kind, ancestors, id)
            entity = client.get(key)

        elif filters:
            print(f"Haetaan {kind} parametreilla:lla: {filters}")
            query = client.query(kind=kind)
            for k,v in filters.items():
                query.add_filter(k, '=', v)

            # pakataan vastaus iteraattoriin
            query_iter = iter(query.fetch())

            # palautetaan ensimmäinen osuma tai None
            entity = next(query_iter, None)

        print(entity)

        return entity if entity else None


    def hae_monta(self, kind: str, ancestors: dict = None, filters: dict = None) -> List[Entity]:
        """ Suorittaa tietokantaan monta riviä palauttavan haun. """

        client = self.avaa_yhteys()

        if ancestors:
            args = []
            for anc_kind, anc_id in ancestors.items():
                args.append(anc_kind)
                args.append(anc_id)

            ancestor_key = client.key(*args)
            print(f"Haetaan monta: {kind} vanhemmilla:lla: {ancestor_key}")
            query = client.query(kind=kind, ancestor=ancestor_key)
        else:
            query = client.query(kind=kind)

        if filters:
            print(f"Haetaan monta: {kind} parametreilla:lla: {filters}")
            for k,v in filters.items():
                query.add_filter(k, '=', v)

        return list(query.fetch())


    def kirjoita(self, kind: str, obj: object, id: int = None, ancestors: dict = None) -> int:
        """ Suorittaa tietokantaan kirjoitusoperaation. Kirjoitusoperaatiot 
        kommitoidaan automaattisesti"""

        client = self.avaa_yhteys()

        print(f"Lisätään {kind}...")

        key = self._rakenna_avain(client, kind, ancestors, id)

        print(f"Avain: {key}")

        if id:
            entity = client.get(key)
        else:
            entity = Entity(key)

        entity.update(obj)

        client.put(entity)

        print(entity)

        return entity.id


    def poista(self, kind: str, id: int, ancestors: dict = None, ):

        client = self.avaa_yhteys()

        print(f"Poistetaan {kind}...")

        key = self._rakenna_avain(client, kind, ancestors, id)

        client.delete(key)


    def _rakenna_avain(self, client: Client, kind: str, ancestors: dict = None, id: int = None):
        print(id, kind, ancestors)
        key_path = []
        
        # yleisin ensin
        if ancestors:
            for anc_kind, anc_id in ancestors.items():
                key_path.append(anc_kind)
                key_path.append(anc_id)

        key_path.append(kind)
        if id:
            key_path.append(id)
        
        return client.key(*key_path)


    # def tee_kutsu(self, query: str, params: dict = None, commit: bool = False) -> Union[Cursor,MySQLCursorBufferedDict]:
    #     """ Delegoi tietokantakutsun tietokantakohteiselle toteutukselle. """
    #     con = self.avaa_yhteys()

    #     vastaus = self.db.tee_kutsu(con, query, params)

    #     # päätetään kirjoitusoperaation transaktio
    #     # commit on oletuksena False jotta ei kutsuta turhaan lukuoperaatioissa
    #     if commit:
    #         con.commit()
    #     return vastaus



class DevDatastore(Database):

    def __init__(self, app):
        os.environ["DATASTORE_PROJECT_ID"] = "emulated-project"
        self.init_test_db()


    def avaa_yhteys(self) -> Client:
        client = Client(
            project="emulated-project",
            namespace='ns_test',
            credentials=None
        )

        return client


    def init_test_db(self):
        emulator_path = os.getenv('DATASTORE_EMULATOR_HOST')
        requests.post('http://' + emulator_path + '/reset')

        client = self.avaa_yhteys()
        with open(os.path.join(os.getcwd(), 'data', 'data.json')) as data:
            KILPAILUT = json.load(data)


            for kilpailu in KILPAILUT:
                child_entities = []
                
                parent_key = client.key("kilpailu")
                parent_entity = Entity(parent_key)

                for k, v in kilpailu.items():
                    if k == 'sarjat' or k == 'rastit':
                        continue
                    elif k == 'alkuaika' or k == 'loppuaika':
                        v = datetime.fromisoformat(v)
                    parent_entity.update({k: v})
                
                client.put(parent_entity)

                for sarja in kilpailu.get('sarjat'):
                    child_key = client.key("sarja", parent=parent_entity.key)
                    child_entity = Entity(child_key)

                    child_entity.update(**sarja)

                    child_entities.append(child_entity)

                for rasti in kilpailu.get('rastit'):
                    child_key = client.key("rasti", parent=parent_entity.key)
                    child_entity = Entity(child_key)

                    child_entity.update(**rasti)

                    child_entities.append(child_entity)

                client.put_multi(child_entities)

                print(parent_entity)



class ProdDatastore(Database):

    def __init__(self, app):
        pass

    def avaa_yhteys(self) -> Client:
        client = Client()
        return client
