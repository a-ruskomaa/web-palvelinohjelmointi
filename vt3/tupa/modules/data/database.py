import sqlite3
from sqlite3.dbapi2 import Cursor, Row
from typing import List
from flask import g

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

        # haetaan tietokannan polku asetuksista
        db_path = app.config['DB_PATH']

        # tietokantayhteys katkaistaan automaattisesti käsitellyn HTTP-pyynnön jälkeen
        app.teardown_appcontext(self.sulje_yhteys)

        # valitaan tietokanta suoritusympäristön perusteella
        if app.env == 'development':
            self.db = SqliteDb(db_path)
        else:
            self.db = MySQLDb(db_path)


    def avaa_yhteys(self):
        """ Avaa tietokantayhteyden. Saman pyynnön aikana
        suoritetut tietokantakutsut suoritetaan samaa
        yhteyttä hyödyntäen. """

        # jos pyynnön aikana ei ole vielä avattu yhteyttä, avataan nyt
        if 'db_conn' not in g:
            print("DB connection opened")
            g.db_conn = self.db.avaa_yhteys()

        # palautetaan yhteys asiakkaan käyttöön
        return g.db_conn


    def sulje_yhteys(self, e=None):
        """ Sulkee tietokantayhteyden. Yhteys
        suljetaan automaattisesti pyynnön kontekstin
        purun aikana, joten yhteyden sulkeminen käsin
        on tarpeen vain poikkeustilanteissa. """

        db_conn = g.pop('db_conn', None)

        if db_conn is not None:
            print("DB connection closed")
            db_conn.close()


    def hae_monta(self, query: str, params: dict = None) -> List[Row]:
        """ Suorittaa tietokantaan monta riviä palauttavan haun. """

        cur = self._tee_kutsu(query, params)
        vastaus = cur.fetchall()
        cur.close()

        return vastaus


    def hae_yksi(self, query: str, params: dict = None) -> Row:
        """ Suorittaa tietokantaan yhden rivin palauttavan haun. """

        cur = self._tee_kutsu(query, params)
        vastaus = cur.fetchone()
        cur.close()

        return vastaus


    def kirjoita(self, query: str, params: dict = None) -> int:
        """ Suorittaa tietokantaan kirjoitusoperaation. """

        cur = self._tee_kutsu(query, params)
        vastaus = cur.lastrowid

        return vastaus


    def _tee_kutsu(self, query: str, params: dict = None) -> Cursor:
        """ Suorittaa tietokantaan halutun kutsun parametreilla tai ilman.
        Parametreja ei tarkisteta, vaan niiden on vastattava kutsua."""
        con = self.avaa_yhteys()
        
        if params:
            return con.execute(query, params)
        else:
            return con.execute(query)


class SqliteDb(Database):

    def __init__(self, path:str):
        self.path = path


    def avaa_yhteys(self):
        conn = sqlite3.connect(self.path, isolation_level=None)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        self.conn = conn
        return conn


    def sulje_yhteys(self):
        if self.conn is not None:
            self.conn.close()


class MySQLDb(Database):
    def __init__(self, path:str):
        self.path = path

    def avaa_yhteys(self):
        pass

    def sulje_yhteys(self):
        pass