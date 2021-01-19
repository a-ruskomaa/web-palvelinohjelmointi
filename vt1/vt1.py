import json
from flask import Flask, Response
app = Flask(__name__)

@app.route('/')
def hello_world():
    return Response('Hello, World!', mimetype="text/plain;charset=UTF-8")

def 