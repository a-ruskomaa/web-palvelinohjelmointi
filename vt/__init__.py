from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)

    # rekisteröidään viikkotehtävien polut blueprinteina selkeyttämään koodia
    from . import vt1
    app.register_blueprint(vt1.bp)

    @app.route('/')
    def hello():
        # luodaan etusivulle linkit viikkotehtävien alasivuille
        rows = []
        for i in range(1,2):
            rows.append(f"<p><a href='/vt{i}/'>Viikkotehtävä {i}</a></p>")
        return "\n".join(rows)
        
    return app