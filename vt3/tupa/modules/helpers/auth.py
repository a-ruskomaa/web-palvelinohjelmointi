import hashlib
from typing import Any
from .errors import AuthenticationError


def tarkista_salasana(hash: str, salasana: str, feed: Any):
    """ Luo selkokielisenä annetusta salasanasta tiivisteen annetulla lisäsyötteellä
    (tässä tapauksessa annettava joukkueen id) ja vertaa saatua tiivistettä
    argumenttina annettuun. """

    hashatty_salasana = hashaa_salasana(feed, salasana)

    if hashatty_salasana != hash:
        raise AuthenticationError("Väärä salasana")


def hashaa_salasana(feed: Any, salasana: str) -> str:
    """ Luo selkokielisenä annetusta salasanasta tiivisteen annetulla lisäsyötteellä
    (tässä tapauksessa annettava joukkueen id)"""

    m = hashlib.sha512()
    m.update( str(feed).encode("UTF-8") )
    m.update( str(salasana).encode("UTF-8") )
    return m.hexdigest()