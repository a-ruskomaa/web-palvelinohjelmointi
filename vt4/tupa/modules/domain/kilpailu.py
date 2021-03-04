from datetime import datetime

# jäi käyttämättä, mutta pidetään tallessa tulevaa varten
class Kilpailu:

    def __init__(self,
            id: int = -1,
            nimi: str = "",
            alkuaika: datetime = None,
            loppuaika: datetime = None,
            kesto: int = 0):
        self.id = id
        self.nimi = nimi
        self.alkuaika = {None if not alkuaika else
                        alkuaika if isinstance(alkuaika, datetime)
                        else datetime.fromisoformat(alkuaika)}
        self.loppuaika = {None if not loppuaika else
                        loppuaika if isinstance(loppuaika, datetime)
                        else datetime.fromisoformat(loppuaika)}
        self.kesto = kesto