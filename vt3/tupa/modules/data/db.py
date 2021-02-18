import sqlite3
import os
from flask import current_app, g
from flask.cli import with_appcontext

DB_PATH = os.path.join(os.getcwd(), 'data', 'data.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()