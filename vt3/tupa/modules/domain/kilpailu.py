from datetime import datetime

class Kilpailu:

    def __init__(self,
            id: int = -1,
            nimi: str = "",
            alkuaika: datetime = datetime.fromtimestamp(0),
            loppuaika: datetime = datetime.fromtimestamp(0),
            kesto: int = 0):
        self.id = id
        self.nimi = self._tarkista_nimi(nimi)
        self.alkuaika = alkuaika if isinstance(alkuaika, datetime) else datetime.fromisoformat(alkuaika)
        self.loppuaika = loppuaika if isinstance(loppuaika, datetime) else datetime.fromisoformat(loppuaika)
        self.kesto = kesto