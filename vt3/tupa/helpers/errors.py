class CustomValidationError(Exception):
    """Heitetään kun validointi epäonnistuu"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def from_arguments(expression, argument):
        """Apumetodi poikkeuksen viestin luomiseksi:
        \"Virheellinen arvo kentässä '{argument}': {expression}\""""
        return CustomValidationError(message = f"Virheellinen arvo kentässä '{argument}': {expression}")


class AuthenticationError(Exception):
    """Heitetään kun kirjautuminen epäonnistuu"""

    # TODO lisää käyttäjä?
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)