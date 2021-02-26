from tupa.modules.domain.kilpailu import Kilpailu

# jäi käyttämättä, mutta pidetään tallessa tulevaa varten
class Rasti:
    
    def __init__(self,
            id: int = -1,
            koodi: str = "",
            lon: float = 0.0,
            lat: float = 0.0,
            kilpailu: Kilpailu = None):
        self.id = id
        self.koodi = koodi
        self.lon = lon
        self.lat = lat
        self.kilpailu = kilpailu
