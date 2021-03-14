import json
import os
from datetime import datetime
from typing import List, Union
from flask import g
from google.cloud.datastore.client import Client
from google.cloud.datastore.entity import Entity
from google.cloud.datastore.key import Key

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
        """ Alustaa tietokannan. """

        # asetetaan tietokantayhteys katkeamaan automaattisesti käsitellyn HTTP-pyynnön jälkeen
        app.teardown_appcontext(self.sulje_yhteys)

        # alustetaan tarvittaessa testitietokanta
        if app.env == 'development':
            client = Client()
            query = client.query(kind='kilpailu')
            query.keys_only()
            if len(list(query.fetch())) == 0:
                self._init_test_db()


    def avaa_yhteys(self) -> Client:
        """ Avaa tietokantayhteyden. Saman pyynnön aikana
        suoritetut tietokantakutsut suoritetaan samaa
        yhteyttä hyödyntäen. """

        # ensimmäinen tietokantakutsu avaa uuden yhteyden
        if 'db_conn' not in g:
            g.db_conn = Client()

        # palautetaan yhteys asiakkaan käyttöön
        return g.db_conn


    def sulje_yhteys(self, e=None):
        """ Sulkee tietokantayhteyden. Yhteys
        suljetaan automaattisesti pyynnön kontekstin
        purun aikana, joten yhteyden sulkeminen käsin
        on tarpeen vain poikkeustilanteissa. """

        db_conn = g.pop('db_conn', None)


    def hae_yksi(self, kind: str, id: int = None, ancestors: dict = None, filters: dict = None) -> Union[Entity, None]:
        """ Suorittaa tietokantaan yhden rivin palauttavan haun. Rivi voidaan etsiä
        id:n ja vanhempien perusteella, tai etsimiseen voidaan käyttää filters-hakemistoa
        jolloin tietokannasta etsitään rivejä joiden attribuutit vastaavat hakemistossa
        annettuja attribuutteja, esim. {'nimi': "Kintturogaining'}. """

        client = self.avaa_yhteys()
        
        # etsitään ensisijaisesti id:n perusteella
        if id:
            key = self._rakenna_avain(client, kind, ancestors, id)
            entity = client.get(key)
        
        # jos avainta ei annettu, etsitään filttereiden perusteella
        elif filters:
            query = client.query(kind=kind)
            for k,v in filters.items():
                query.add_filter(k, '=', v)

            # pakataan vastaus iteraattoriin
            query_iter = iter(query.fetch())

            # palautetaan ensimmäinen osuma tai None
            entity = next(query_iter, None)

        return entity


    def hae_monta(self, kind: str, ancestors: dict = None, filters: dict = None, order: list = None) -> List[Entity]:
        """ Suorittaa tietokantaan monta riviä palauttavan haun. Haku voidaan suorittaa pelkän tyypin
        perusteella, tai hakuun voidaan liittää muita rajausehtoja. Hakutulokset voi myös järjestää
        order-parametrina annettavan listan mukaisten atribuuttien mukaiseen järjestykseen."""

        client = self.avaa_yhteys()

        query = client.query(kind=kind)

        # Lisätään kyselyyn haetun alkion vanhemmat.
        if ancestors:
            key_args = []

            # Vanhemmat tulee antaa järjestyksessä siten, että "vanhin" on
            # ensimmäisenä alkiona. Ei toimi vanhemmilla python-versioilla,
            # joissa hakemiston järjestys ei ole pysyvä.
            for anc_kind, anc_id in ancestors.items():
                key_args.append(anc_kind)
                key_args.append(anc_id)

            query.ancestor = client.key(*key_args)

        # lisätään järjestysehto
        if order:
            query.order = order

        # lisätään muut rajausehdot
        if filters:
            for k,v in filters.items():
                query.add_filter(k, '=', v)

        res = list(query.fetch())

        return res


    def kirjoita(self, kind: str, obj: object, id: int = None, ancestors: dict = None) -> int:
        """ Suorittaa tietokantaan kirjoitusoperaation. Jos tunnisteeksi annetaan alkion
        id, päivitetään aiempi alkio."""

        client = self.avaa_yhteys()
        key = self._rakenna_avain(client, kind, ancestors, id)

        entity = None

        # jos id on annettu, haetaan päivitettävä alkio
        if id:
            entity = client.get(key)

        # tarvittaessa luodaan uusi alkio
        if not entity:
            entity = Entity(key)

        # lisätään päivitetty alkio tietokantaan
        entity.update(obj)
        client.put(entity)

        return entity.id


    def poista(self, kind: str, id: int, ancestors: dict = None, ):
        """ Poistaa alkion tietokannasta. Tunnisteeksi annettava alkion
        id ja mahdolliset vanhemmat. """

        client = self.avaa_yhteys()

        key = self._rakenna_avain(client, kind, ancestors, id)

        client.delete(key)


    def _rakenna_avain(self, client: Client, kind: str, ancestors: dict = None, id: int = None) -> Key:
        """ Apufunktio, joka luo alkiolle avaimen annetun tyypin ja mahdollisen id:n ja vanhempien
        perusteella. """

        key_path = []

        # Vanhemmat tulee antaa järjestyksessä siten, että "vanhin" on
        # ensimmäisenä alkiona. Ei toimi vanhemmilla python-versioilla,
        # joissa hakemiston järjestys ei ole pysyvä.
        if ancestors:
            for anc_kind, anc_id in ancestors.items():
                key_path.append(anc_kind)
                key_path.append(anc_id)

        # Lisätään avaimen polkuun haetun alkion tyyppi
        key_path.append(kind)

        # jos id annettu, lisätään myös se
        if id:
            key_path.append(id)
        
        return client.key(*key_path)



    def _init_test_db(self):
        """ Lisää annetun testidatan tietokantaan """

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
