from flask import Response

def return_text(view):
    def wrapped_view(*args, **kwargs):
        return Response(view(*args, **kwargs), mimetype="text/plain;charset=UTF-8")

    return wrapped_view