from datetime import datetime
import json
import os
import requests
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
            self.init_test_db(self.db)
        else:
            self.db = ProdDatastore(app)


    def init_test_db(self, db):
        emulator_path = os.getenv('DATASTORE_EMULATOR_HOST')
        requests.post('http://' + emulator_path + '/reset')

        client = db.avaa_yhteys()
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


    def hae_yksi(self, kind: str, id: int = None, params: dict = None):
        """ Suorittaa tietokantaan yhden rivin palauttavan haun. """

        client = self.avaa_yhteys()

        if id:
            entity_key = client.key(kind, id)

            entity = client.get(entity_key)

        elif params:
            query = client.query(kind=kind)
            for k,v in params.items():
                query.add_filter(k, '=', v)

            # pakataan vastaus iteraattoriin
            query_iter = iter(query.fetch())

            # palautetaan ensimmäinen osuma tai None
            entity = next(query_iter, None)

        return entity


    def hae_monta(self, kind: str, ancestor: dict = None, params: dict = None) -> List:
        """ Suorittaa tietokantaan monta riviä palauttavan haun. """

        client = self.avaa_yhteys()

        if ancestor:
            ancestor_key = client.key(ancestor.get('kind'), ancestor.get('id'))
            query = client.query(kind=kind, ancestor=ancestor_key)
        else:
            query = client.query(kind=kind)

        if params:
            for k,v in params.items():
                query.add_filter(k, '=', v)

        return list(query.fetch())


    # def kirjoita(self, query: str, params: dict = None, commit: bool = True) -> int:
    #     """ Suorittaa tietokantaan kirjoitusoperaation. Kirjoitusoperaatiot 
    #     kommitoidaan automaattisesti.
        
    #     Koska tietokantayhteys on HTTP-pyyntökohtainen, voidaan samaan transaktioon liittää
    #     useita kirjoitusoperaatioita asettamalla parametriksi commit=False. Viimeisen operaation
    #     tulee tällöin huolehtia transaktion kommitoinnista."""

    #     cur = self.tee_kutsu(query, params, commit)
    #     vastaus = cur.lastrowid
    #     return vastaus


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


    def avaa_yhteys(self) -> Client:
        client = Client(
            project="emulated-project",
            namespace='ns_test',
            credentials=None
        )

        return client


    # def sulje_yhteys(self):
    #     if self.conn is not None:
    #         self.conn.close()


    # def tee_kutsu(self, con, query: str, params: dict = None) -> Cursor:
    #     """ Suorittaa tietokantaan halutun kutsun parametreilla tai ilman.
    #     Parametreja ei tarkisteta, vaan niiden on vastattava kutsua."""
    #     try:
    #         if params:
    #             return con.execute(self._convert_query(query), params)
    #         else:
    #             return con.execute(self._convert_query(query))
    #     except Exception as e:
    #         print(f"***** DATABASE ERROR: *****")
    #         print(e)
    #         raise


class ProdDatastore(Database):

    def __init__(self, app):
        pass

    def avaa_yhteys(self) -> Client:
        client = Client()
        return client


    # def sulje_yhteys(self):
    #     self.cnx.close()


    # def tee_kutsu(self, cnx, query: str, params: dict = None) -> Cursor:
    #     """ Suorittaa tietokantaan halutun kutsun parametreilla tai ilman. """

    #     cursor = cnx.cursor(dictionary=True, buffered=True)
        
    #     if params:
    #         cursor.execute(query, params)
    #     else:
    #         cursor.execute(query)
            
    #     return cursor
