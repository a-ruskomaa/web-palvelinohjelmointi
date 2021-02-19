
import os
from tupa.modules.data.db import Database, MySQLDb, SqliteDb
from flask import g

DB_PATH = os.path.join(os.getcwd(), 'data', 'data.db')

db = None

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
        g.db = db.get_connection()

    return g.db


def close_connection(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

