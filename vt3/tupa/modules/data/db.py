import sqlite3
from flask import g

class Database:
    def get_connection(self):
        pass
    def close_connection(self):
        pass

class SqliteDb(Database):

    def __init__(self, path:str):
        self.path = path

    def get_connection(self):
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        self.conn = conn
        return conn

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()

class MySQLDb(Database):
    def get_connection(self):
        pass
    def close_connection(self):
        pass