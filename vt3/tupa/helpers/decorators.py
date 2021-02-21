from flask import Response, session, redirect, url_for
from typing import List
from functools import wraps

def roles_allowed(roles: List[str]):
    """Decorator that only allows access to a route if the user is logged in and has at least
    one of the specified roles"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = session.get('kayttaja')
            if not user:
                print("no user")
                return redirect(url_for('auth.login'))
            if any(role in user['roolit'] for role in roles):
                # User has a required role, route request back to the original handler
                print("correct role")
                return func(*args, **kwargs)
            else:
                print("wrong role")
                return redirect(url_for('index'))

        return wrapper
    return decorator
