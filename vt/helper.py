from flask import Response


def return_text(func):
    """ decorator, joka estää flaskia muuntamasta vastausta html-koodiksi """
    def wrapped_response(*args, **kwargs):
        # lisätään alkuperäisen funktiokutsun vastaus Responsen ensimmäiseksi argumentiksi
        return Response(func(*args, **kwargs), mimetype="text/plain;charset=UTF-8")

    return wrapped_response