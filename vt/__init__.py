from flask import Flask

def create_app():
    app = Flask(__name__)

    # rekisteröidään viikkotehtävien polut blueprinteina selkeyttämään koodia
    from .views.vt1 import vt1
    app.register_blueprint(vt1)

    @app.route('/')
    def hello():
        # luodaan etusivulle linkit viikkotehtävien alasivuille
        rows = []
        for i in range(1,2):
            rows.append(f"<p><a href='/vt{i}/'>Viikkotehtävä {i}</a></p>")
        return "\n".join(rows)
        
    return app

# if __name__ == '__main__':
#     # asetetaan debug-moodi päälle. Ei saa pitää päällä tuotantokäytössä
#     app = create_app()
#     app.debug = True
#     app.run()