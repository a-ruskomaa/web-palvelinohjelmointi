from flask import Response

def return_text(func):
    def wrapped_response(*args, **kwargs):
        return Response(func(*args, **kwargs), mimetype="text/plain;charset=UTF-8")

    return wrapped_response