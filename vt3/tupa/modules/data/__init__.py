
import os
from tupa.modules.data.db import Database, MySQLDb, SqliteDb
from flask import g

DB_PATH = os.path.join(os.getcwd(), 'data', 'data.db')

db = None

# TODO init within app context
def init_db(app):
    global db
    # if app.env == 'development':
    print("initializing sqlite")
    db = SqliteDb(DB_PATH)
    # else:
        # print("initializing mysql")
        # db = MySQLDb()


def get_connection():
    if 'db' not in g:
        print("DB connection opened")
        g.db = db.get_connection()

    return g.db


def close_connection(e=None):
    print("DB connection closed")
    db = g.pop('db', None)

    if db is not None:
        db.close()


def hae_monta(query: str = None, params: dict = None):
    cur = _tee_kutsu(query, params)

    vastaus = cur.fetchall()
    cur.close()

    return vastaus

def hae_yksi(query: str = None, params: dict = None):
    cur = _tee_kutsu(query, params)

    vastaus = cur.fetchone()
    cur.close()

    return vastaus

def lisaa(query: str = None, params: dict = None):
    cur = _tee_kutsu(query, params)

    vastaus = cur.lastrowid

    return vastaus


def _tee_kutsu(query: str = None, params: dict = None):
    con = get_connection()
    
    if params:
        print("haetaan parametreilla")
        print(params)
        return con.execute(query, params)
    else:
        print("haetaan ilman parametreja")
        return con.execute(query)