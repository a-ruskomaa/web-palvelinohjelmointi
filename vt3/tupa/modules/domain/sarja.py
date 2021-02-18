from tupa.modules.domain.kilpailu import Kilpailu
from datetime import datetime

class Sarja:

    def __init__(self,
                id: int = -1,
                nimi: str = "",
                matka: str = "",
                alkuaika: datetime = datetime.fromtimestamp(0),
                loppuaika: datetime = datetime.fromtimestamp(0),
                kilpailu: Kilpailu = None):
        self.id = id
        self.nimi = self._tarkista_nimi(nimi)
        self.matka = matka
        self.alkuaika = alkuaika if isinstance(alkuaika, datetime) else datetime.fromisoformat(alkuaika)
        self.loppuaika = loppuaika if isinstance(loppuaika, datetime) else datetime.fromisoformat(loppuaika)
        self.kilpailu = kilpailu
