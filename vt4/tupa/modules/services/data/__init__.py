from tupa.modules.services.data.dataservice import DataService
from tupa.modules.services.data.database import Database

# luodaan modulin alustuksen yhteydessä tietokanta, jonka saa käyttöön importtaamalla
db = Database()
ds = DataService(db)