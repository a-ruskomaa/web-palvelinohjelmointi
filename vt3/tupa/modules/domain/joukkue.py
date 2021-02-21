import hashlib
import ast
from tupa.modules.domain.sarja import Sarja
from tupa.helpers.errors import AuthenticationError, CustomValidationError

class Joukkue:
    
    # TODO lisää type error tarkistus konstruktorin kutsuun
    def __init__(self, id: int = -1, nimi: str = "", salasana: str = None, sarja: int = None, jasenet: list = []):
        self.id = id
        self.nimi = self._tarkista_nimi(nimi)
        self.salasana = salasana
        self.sarja = sarja
        if type(jasenet) == str:
            jasenet = ast.literal_eval(jasenet)
        self.jasenet = self._tarkista_jasenet(jasenet)

    
    def _tarkista_jasenet(self, jasenet: list):
        jasenmaara = len(jasenet)
        if not 2 <= jasenmaara <= 5:
            raise CustomValidationError.from_arguments(jasenmaara, 'jäsenet')

        return jasenet


    def _tarkista_nimi(self, nimi: str):
        pituus = len(nimi)
        if pituus == 0:
            raise CustomValidationError("Nimi ei voi olla tyhjä")

        return nimi


    def tarkista_salasana(self, salasana: str):
        pw_hash = self.hashaa_salasana(salasana)

        if pw_hash != self.salasana:
            raise AuthenticationError("Väärä salasana")


    def hashaa_salasana(self, salasana: str) -> str:
        m = hashlib.sha512()
        m.update( str(self.id).encode("UTF-8") )
        m.update( str(salasana).encode("UTF-8") )
        return m.hexdigest()
