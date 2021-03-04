from flask import Response, session, redirect, url_for
from typing import List
from functools import wraps

def sallitut_roolit(roolit: List[str]):
    """Sallii vain annetuissa rooleissa oleville käyttäjille pääsyn tällä koristeltuun reittiin."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Haetaan kirjautunut käyttäjä sessiosta
            kayttaja = session.get('kayttaja')
            # Jos ei käyttäjää, uudelleenohjataan kirjautumissivulle
            if not kayttaja:
                return redirect(url_for('auth.login'))
            # Jos on käyttäjä ja käyttäjällä on vaadittu rooli, päästetään jatkamaan
            if any(rooli in kayttaja['roolit'] for rooli in roolit):
                return func(*args, **kwargs)
            # Jos ei oikeaa roolia, ohjataan etusivulle
            else:
                return redirect(url_for('index'))

        return wrapper
    return decorator
