import sqlite3
from flask import g

class Database:

    def __init__(self, app = None) -> None:
        self.app = app
        if app is not None:
            self.init_app(app)
    

    def init_app(self, app):
        db_path = app.config['DB_PATH']
        app.teardown_appcontext(self.close_connection)

        if app.env == 'development':
            self.db = SqliteDb(db_path)
        else:
            self.db = MySQLDb(db_path)


    def get_connection(self):
        if 'db_conn' not in g:
            print("DB connection opened")
            g.db_conn = self.db.get_connection()

        return g.db_conn


    def close_connection(self, e=None):
        db_conn = g.pop('db_conn', None)

        if db_conn is not None:
            print("DB connection closed")
            db_conn.close()


    def hae_monta(self, query: str = None, params: dict = None):
        cur = self._tee_kutsu(query, params)

        vastaus = cur.fetchall()
        cur.close()

        return vastaus


    def hae_yksi(self, query: str = None, params: dict = None):
        cur = self._tee_kutsu(query, params)

        vastaus = cur.fetchone()
        cur.close()

        return vastaus


    def lisaa(self, query: str = None, params: dict = None):
        cur = self._tee_kutsu(query, params)

        vastaus = cur.lastrowid

        return vastaus


    def _tee_kutsu(self, query: str = None, params: dict = None):
        con = self.get_connection()
        
        if params:
            print("haetaan parametreilla")
            print(params)
            return con.execute(query, params)
        else:
            print("haetaan ilman parametreja")
            return con.execute(query)


class SqliteDb(Database):

    def __init__(self, path:str):
        self.path = path


    def get_connection(self):
        conn = sqlite3.connect(self.path, isolation_level=None)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        self.conn = conn
        return conn


    def close_connection(self):
        if self.conn is not None:
            self.conn.close()


class MySQLDb(Database):
    def __init__(self, path:str):
        self.path = path

    def get_connection(self):
        pass

    def close_connection(self):
        pass