from flask import Flask, render_template, session
from flask.helpers import url_for
from werkzeug.utils import redirect

print("initializing app...")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    
    print("creating app...")

    from .views import admin, login
    app.register_blueprint(admin.bp)
    app.register_blueprint(login.bp)

    from tupa.modules.data import init_db
    
    init_db(app)

    @app.route('/', methods=["GET"])
    def index():
        print("ETUSIVU")
        if session.get('joukkue'):
            return redirect(url_for('joukkuesivu'))
        else:
            return redirect(url_for('login.login'))
            
    return app