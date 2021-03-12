from tupa.modules.services.auth.authservice import AuthService
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
authService = AuthService(oauth)