from flask.app import Flask
from flask.helpers import url_for
from tupa.modules.domain.kilpailu import Kilpailu
from werkzeug.utils import redirect
from tupa.modules.domain.joukkue import Joukkue
from urllib.error import URLError
from flask import Blueprint, request, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from tupa.modules.data import hae_monta, hae_yksi
from tupa.helpers.errors import AuthenticationError, CustomValidationError

bp = Blueprint('auth', __name__, url_prefix='')

######## REITIT ########

@bp.route('/login', methods=['GET','POST'])
def login():
    kilpailut = _hae_kilpailut() 
    loginform = _luo_login_form(kilpailut)
    loginerrors = []

    if loginform.validate_on_submit():
        kilpailu_id=loginform.kilpailu.data
        joukkue_nimi=loginform.joukkue.data

        try:
            joukkue_dict = _hae_joukkue(kilpailu_id, joukkue_nimi)
            print("joukkue:")
            print(joukkue_dict)
            if not joukkue_dict:
                raise AuthenticationError("Joukkuetta ei löytynyt")

            joukkue = Joukkue(**joukkue_dict)
            # joukkue.tarkista_salasana(loginform.salasana.data)

            kilpailu_nimi = kilpailut[int(kilpailu_id)]['nimi']
            session['kayttaja'] = {
                'id': joukkue.id,
                'roolit': ['joukkue']
            }
            session['valittu'] = {
                'kilpailu': (kilpailu_id, kilpailu_nimi),
                'sarja': None,
                'joukkue': (joukkue.id, joukkue_nimi)
    
            }
            return redirect(url_for('joukkueet.listaa'))

        except (AuthenticationError):
            loginerrors.append('Kirjautuminen epäonnistui')
        
    return render_template('login/login.html', loginform=loginform, loginerrors=loginerrors)


@bp.route('/logout')
def logout():
    session.pop('kayttaja',None)
    return redirect('/')

######## FORMIT ########


def _luo_login_form(kilpailut: dict) -> FlaskForm:
    kilpailu_tuplet = tuple((kilpailu['id'], kilpailu['nimi']) for kilpailu in kilpailut.values())

    class LoginForm(FlaskForm):
        joukkue = StringField('joukkue', validators=[validators.InputRequired(message='Syötä arvo!')])
        salasana = PasswordField('salasana', validators=[validators.InputRequired(message='Syötä arvo!')])
        kilpailu = RadioField('kilpailu', choices=kilpailu_tuplet, default=str(kilpailu_tuplet[0][0]), validators=[validators.InputRequired(message='Valitse yksi!')])

    return LoginForm()
    

######## KANTAKYSELYT ########

# TODO yhtenästä palautusmuoto

def _hae_kilpailut() -> dict:
    sql = """SELECT nimi, id FROM kilpailut"""

    rivit = hae_monta(sql)
    kilpailut = {}
    for rivi in rivit:
        kilpailut[rivi['id']] = rivi['nimi']
    kilpailut = {rivi['id']:{key:rivi[key] for key in rivi.keys()} for rivi in rivit}
    print("kilpailut:")
    print(kilpailut)
    return kilpailut


def _hae_joukkue(kilpailu_id: int, joukkue_nimi: str) -> dict:
    sql = """SELECT joukkueet.id AS id,
                    joukkueet.nimi AS nimi,
                    joukkueet.salasana AS salasana,
                    joukkueet.sarja AS sarja,
                    joukkueet.jasenet AS jasenet
            FROM joukkueet
            JOIN sarjat ON joukkueet.sarja = sarjat.id
            JOIN kilpailut ON sarjat.kilpailu = kilpailut.id
            WHERE sarjat.kilpailu = :kilpailu_id
            AND trim(upper(joukkueet.nimi))
            = trim(upper(:joukkue_nimi))"""
            
    params = {'kilpailu_id': kilpailu_id,
              'joukkue_nimi': joukkue_nimi}

    rivi = hae_yksi(sql, params)
    return dict(**rivi) if rivi else None