from tupa.modules.helpers.errors import AuthenticationError
from authlib.integrations.flask_client import OAuth

class AuthService:
    def __init__(self, oauth: OAuth):
        self.oauth = oauth


    def init_app(self, app):

        # haetaan avainparametrit sovelluksen konfiguraatiosta
        GOOGLE_CLIENT_ID = app.config.get("GOOGLE_CLIENT_ID")
        GOOGLE_CLIENT_SECRET = app.config.get("GOOGLE_CLIENT_SECRET")

        # rekisteröidään autentikaatiopalvelin. authlib hakee server_metadata_url:n perusteella
        # automaattisesti tarvittavat osoitteet käyttäjän kirjautumista, tokenin verifiointia yms varten
        self.oauth.register(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'email',
                'prompt': 'select_account'
                }
        )

        # luodaan asiakas kirjautumista varten
        self.client = self.oauth.create_client('google')


    def parse_user_from_token(self):
        """ "Parsii käyttäjän sähköpostiosoitteen palvelimen lähettämästä tokenista ja
        palauttaa tiedot hakemistona."""

        try:
            # vahvistetaan palvelimen palauttaman tokenin aitous, authlib huolehtii tokenin
            # ylläpidosta, eikä funktio tarvitse viitettä tokeniin 
            token = self.client.authorize_access_token()
            
            # parsitaan käyttäjän tiedot tokenista
            google_account = self.client.parse_id_token(token)

            # käytetään sähköpostiosoitetta käyttäjän tunnistamiseen
            user = {
                'email': google_account.get('email')
            }

            if not user:
                raise AuthenticationError(f"Account with email {google_account.get('email')} not found ")
        except Exception as e:
            raise e
        
        return user


    def redirect_to_auth_login(self, callback_url):
        """ Uudelleenohjaa pyynnön autentikaatiopalvelimelle """
        return self.client.authorize_redirect(callback_url)