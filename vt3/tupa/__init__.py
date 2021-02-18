from flask import Flask

def create_app():
    app = Flask(__name__)

    from .views.vt3 import vt3
    app.register_blueprint(vt3)

    @app.route('/')
    def hello():
        # luodaan etusivulle linkit viikkotehtävien alasivuille
        rows = []
        for i in range(1,4):
            if i==2: continue
            
            rows.append(f"<p><a href='/vt{i}/'>Viikkotehtävä {i}</a></p>")
        return "\n".join(rows)
        
    return app