from urllib.error import URLError
from flask import Blueprint, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators

import tupa.modules.data.db
from tupa.helpers.decorators import return_text

bp = Blueprint('login', __name__, url_prefix='/login')


from tupa.modules.data import get_connection, close_connection


@bp.route('/', methods=['GET','POST'])
def login():
    kilpailut = _hae_kilpailut()
    loginform = _luo_login_form(kilpailut)

    if loginform.validate_on_submit():
        print("JEI")
        return render_template('test.html')
    else:
        print("NOPE")
        print(loginform.validate())
        print(loginform.joukkue.errors)
        print(loginform.salasana.errors)
        print(loginform.kilpailu.errors)

    return render_template('login.html', loginform=loginform)


def _luo_login_form(kilpailut: dict):
    kilpailu_tuplet = tuple((kilpailu['id'], kilpailu['nimi']) for kilpailu in kilpailut)

    class LoginForm(FlaskForm):
        joukkue = StringField('joukkue', validators=[validators.InputRequired(message='Syötä arvo!')])
        salasana = PasswordField('salasana', validators=[validators.InputRequired(message='Syötä arvo!')])
        kilpailu = RadioField('kilpailu', choices=kilpailu_tuplet)

    return LoginForm()
    

def _hae_kilpailut() -> dict:
    con = get_connection()
    cur = con.cursor()

    sql = """
    SELECT id, nimi
    FROM kilpailut
    """
    cur.execute(sql)
    kilpailut = cur.fetchall()

    close_connection()

    return kilpailut
