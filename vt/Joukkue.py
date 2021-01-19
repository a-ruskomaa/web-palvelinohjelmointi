class Joukkue:
    def __init__(self, nimi: str, jasenet: list=[], id: int=-1, leimaustapa: list=[], rastit: list=[]):
        self.nimi = nimi
        self.jasenet = jasenet
        self.id = id
        self.leimaustapa = leimaustapa
        self.rastit = rastit

    def __str__(self) -> str:
        return str(self.__dict__)