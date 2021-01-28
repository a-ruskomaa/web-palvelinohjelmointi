from flask import Response
from werkzeug.datastructures import Headers


def return_text(func):
    """ decorator, joka estää flaskia muuntamasta vastausta html-koodiksi """
    def wrapped_response(*args, **kwargs):
        # lisätään alkuperäisen funktiokutsun vastaus Responsen ensimmäiseksi argumentiksi
        return Response(func(*args, **kwargs), content_type="text/plain;charset=UTF-8")

    return wrapped_response