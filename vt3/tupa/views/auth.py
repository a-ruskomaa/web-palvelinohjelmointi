from flask import Blueprint, render_template, session, redirect
from flask.helpers import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from tupa.modules.domain.joukkue import Joukkue
from tupa.modules.data.dataservice import hae_kilpailut, hae_joukkue_nimella
from tupa.helpers.errors import AuthenticationError

bp = Blueprint('auth', __name__, url_prefix='')

######## REITIT ########

@bp.route('/login', methods=['GET','POST'])
def login():
    kilpailut = hae_kilpailut() 
    loginform = _luo_login_form(kilpailut)
    loginerrors = []

    if loginform.validate_on_submit():
        kilpailu_id=loginform.kilpailu.data
        joukkue_nimi=loginform.joukkue.data

        try:
            joukkue_dict = hae_joukkue_nimella(kilpailu_id, joukkue_nimi)
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

@bp.route('/admin/login')
def admin_login():
    pass

@bp.route('/logout')
def logout():
    session.pop('kayttaja', None)
    return redirect('/')

######## FORMIT ########


def _luo_login_form(kilpailut: dict) -> FlaskForm:
    kilpailu_tuplet = tuple((kilpailu['id'], kilpailu['nimi']) for kilpailu in kilpailut.values())

    class LoginForm(FlaskForm):
        joukkue = StringField('joukkue', validators=[validators.InputRequired(message='Syötä arvo!')])
        salasana = PasswordField('salasana', validators=[validators.InputRequired(message='Syötä arvo!')])
        kilpailu = RadioField('kilpailu', choices=kilpailu_tuplet, default=str(kilpailu_tuplet[0][0]), validators=[validators.InputRequired(message='Valitse yksi!')])

    return LoginForm()
    