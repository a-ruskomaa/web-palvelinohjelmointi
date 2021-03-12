from tupa.modules.helpers.errors import AuthenticationError
from authlib.integrations.flask_client import OAuth


class AuthService:
    def __init__(self, oauth: OAuth):
        self.oauth = oauth


    def init_app(self, app):

        # If running on local machine or testing environment, get them from env variables
        GOOGLE_CLIENT_ID = app.config.get("GOOGLE_CLIENT_ID")
        GOOGLE_CLIENT_SECRET = app.config.get("GOOGLE_CLIENT_SECRET")

        # TODO handling the situation when client id and secret are not set,
        # or the auth server does not respond

        # Registers the identity provider. Authlib will automatically retrieve the correct endpoints
        # for authenticating, fetching and authorizing the token, etc from the server_metadata_url.
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

        # Create the actual client with the registered information
        self.client = self.oauth.create_client('google')


    def parse_user_from_token(self):
        """Parses the identity information received from the auth provider and 
        stores it inside the session context"""
        try:
            # OAuth server sends an authorization code to the callback url that
            # was specified in the initial call to /login. Behind the scenes,
            # authlib grabs the authorization code from the request context and
            # exchanges it to a valid token with another request to the auth provider
            token = self.client.authorize_access_token()
            

            # The scope of information received from the auth provider is specified
            # by the 'scope' keyword when registering the oauth client. Here we
            # id the user simply based on their email address 
            google_account = self.client.parse_id_token(token)

            user = {
                'email': google_account.get('email')
            }

            if not user:
                raise AuthenticationError(f"Account with email {google_account.get('email')} not found ")
        except Exception as e:
            raise e
        
        return user


    def redirect_to_auth_login(self, callback_url):
        """Creates the url the end-user will be redirected for authentication.
        :param callback_url is the url that the auth server will access to continue
        with the authentication process."""
        return self.client.authorize_redirect(callback_url)