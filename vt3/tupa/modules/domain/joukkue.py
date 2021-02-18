from tupa.modules.domain.sarja import Sarja
from tupa.helpers.errors import ValidationError

class Joukkue:
    
    def __init__(self, id: int = -1, nimi: str = "", sarja: Sarja = None, jasenet: list = []):
        self.id = id
        self.nimi = self._tarkista_nimi(nimi)
        self.sarja = sarja
        self.jasenet = self._tarkista_jasenet(jasenet)

    
    def _tarkista_jasenet(self, jasenet: list):
        jasenmaara = len(jasenet)
        if not 2 <= jasenmaara <= 5:
            raise ValidationError.from_arguments('jäsenet', jasenmaara)

        return jasenet

    def _tarkista_nimi(self, nimi: str):
        pituus = len(nimi)
        if pituus == 0:
            raise ValidationError("Nimi ei voi olla tyhjä")

        # if toinen samanniminen joukkue sarjassa
        # 
        return nimi 