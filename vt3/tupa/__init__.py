from flask import Flask, render_template

print("initializing app...")

def create_app():
    app = Flask(__name__)
    
    print("creating app...")

    from .views import admin
    app.register_blueprint(admin.bp)

    from tupa.modules.data import init_db, get_connection, close_connection

    init_db(app)

    @app.route('/', methods=['GET'], strict_slashes=False)
    def index():
        con = get_connection()
        cur = con.cursor()

        sql = """
        SELECT nimi
        FROM kilpailut
        """
        cur.execute(sql)
        kilpailut = cur.fetchall()
        return render_template('index.html', kilpailut=kilpailut)
            
    return app