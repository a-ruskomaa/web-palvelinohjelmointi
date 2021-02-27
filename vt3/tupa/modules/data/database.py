import sqlite3
from flask.globals import current_app
import mysql.connector
from mysql.connector.cursor import MySQLCursorBufferedDict
import mysql.connector.pooling
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

        # tietokantayhteys katkaistaan automaattisesti käsitellyn HTTP-pyynnön jälkeen
        app.teardown_appcontext(self.sulje_yhteys)

        # valitaan tietokanta suoritusympäristön perusteella
        if app.env == 'development':
            self.db = SqliteDb(app)
        else:
            self.db = MySQLDb(app)


    def avaa_yhteys(self):
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

        if db_conn is not None:
            db_conn.close()


    def hae_monta(self, query: str, params: dict = None) -> List[Row]:
        """ Suorittaa tietokantaan monta riviä palauttavan haun. """

        cur = self.tee_kutsu(query, params)
        vastaus = cur.fetchall()
        cur.close()

        return vastaus


    def hae_yksi(self, query: str, params: dict = None) -> Row:
        """ Suorittaa tietokantaan yhden rivin palauttavan haun. """

        cur = self.tee_kutsu(query, params)
        vastaus = cur.fetchone()
        cur.close()

        return vastaus


    def kirjoita(self, query: str, params: dict = None, commit: bool = True) -> int:
        """ Suorittaa tietokantaan kirjoitusoperaation. Kirjoitusoperaatiot 
        kommitoidaan automaattisesti.
        
        Koska tietokantayhteys on HTTP-pyyntökohtainen, voidaan samaan transaktioon liittää
        useita kirjoitusoperaatioita asettamalla parametriksi commit=False. Viimeisen operaation
        tulee tällöin huolehtia transaktion kommitoinnista."""

        cur = self.tee_kutsu(query, params, commit)
        vastaus = cur.lastrowid
        return vastaus


    def tee_kutsu(self, query: str, params: dict = None, commit: bool = False) -> MySQLCursorBufferedDict:
        """ Delegoi tietokantakutsun tietokantakohteiselle toteutukselle. 
        'Autocommit' on pois päältä jottei sitä turhaan kutsuta lukuoperaatoissa."""
        con = self.avaa_yhteys()

        vastaus = self.db.tee_kutsu(con, query, params)

        # Päätetään kirjoitusoperaation transaktio
        if commit:
            con.commit()
        return vastaus



class SqliteDb(Database):

    def __init__(self, app):
        # haetaan tietokannan polku asetuksista
        self.path = app.config['DB_PATH']


    def _convert_query(self, query: str) -> str:
        """ Muuntaa sql-merkkijonon parametrit SQLiten ymmärtämään muotoon """
        return query.replace('%s', '?')


    def avaa_yhteys(self):
        """ Avaa yhteyden paikalliseen SQLite-tietokantaan """
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        self.conn = conn
        return conn


    def sulje_yhteys(self):
        if self.conn is not None:
            self.conn.close()


    def tee_kutsu(self, con, query: str, params: dict = None) -> Cursor:
        """ Suorittaa tietokantaan halutun kutsun parametreilla tai ilman.
        Parametreja ei tarkisteta, vaan niiden on vastattava kutsua."""
        try:
            if params:
                return con.execute(self._convert_query(query), params)
            else:
                return con.execute(self._convert_query(query))
        except Exception as e:
            print(f"***** DATABASE ERROR: *****")
            print(e)
            raise


class MySQLDb(Database):

    def __init__(self, app):
        """ Alustaa asetukset yhteyden ottamiseksi MySQL-tietokantaan """
        self.config = {
            "database": app.config.get('DB_NAME'),
            "user": app.config.get('DB_USER'),
            "passwd": app.config.get('DB_PW'),
            "host": app.config.get('DB_HOST')
        }


    def avaa_yhteys(self):
        """ Avaa yhteyden MySQL-tietokantaan """
        self.cnx = mysql.connector.connect(**self.config)
        return self.cnx


    def sulje_yhteys(self):
        """ Sulkee yhteyden MySQL-tietokantaan """
        self.cnx.close()


    def tee_kutsu(self, cnx, query: str, params: dict = None) -> Cursor:
        """ Suorittaa tietokantaan halutun kutsun parametreilla tai ilman. """

        cursor = cnx.cursor(dictionary=True, buffered=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        return cursor
