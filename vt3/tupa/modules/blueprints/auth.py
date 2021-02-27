from flask import Blueprint, render_template, session, redirect
from flask.globals import current_app, request
from flask.helpers import url_for
from tupa.modules.data.dataservice import hae_kilpailut, hae_joukkue_nimella
from tupa.modules.helpers.errors import AuthenticationError
from tupa.modules.helpers.auth import tarkista_salasana
from tupa.modules.helpers.forms import UserLoginForm, AdminLoginForm

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/joukkue/login', methods=['GET','POST'])
def login():
    """Reitti, jonka kautta joukkueet kirjautuvat sovellukseen"""

    # luodaan kirjautumislomake
    loginform = UserLoginForm()

    # haetaan kilpailut tietokannasta ja muokataan ne tupleiksi
    kilpailut = hae_kilpailut() 
    kilpailu_tuplet = [(kilpailu['id'], kilpailu['nimi']) for kilpailu in kilpailut.values()]

    # lisätään lomakkeelle kilpailut vaihtoehdoiksi
    loginform.kilpailu.choices = kilpailu_tuplet

    # valitaan ensimmäinen vaihtoehto
    if request.method == 'GET':
        loginform.kilpailu.data = kilpailu_tuplet[0][0]

    loginerrors = []

    # tarkistetaan formi
    if loginform.validate_on_submit():
        kilpailu_id=loginform.kilpailu.data
        joukkue_nimi=loginform.kayttaja.data

        try:
            # etsitään onko valitussa kilpailussa annetun nimistä joukkuetta
            joukkue = hae_joukkue_nimella(kilpailu_id, joukkue_nimi)

            if not joukkue:
                raise AuthenticationError("Joukkuetta ei löytynyt")

            # tarkistetaan annettu salasana, funktio heittää AuthenticationError:n jos salasana on väärä
            tarkista_salasana(joukkue['salasana'], loginform.salasana.data, joukkue['id'])

            # tallennetaan käyttäjän tiedot sessioon
            session['kayttaja'] = {
                'id': joukkue['id'],
                'roolit': ['joukkue']
            }

            # tallennetaan sessioon tieto valinnoista, valittu joukkue = sisäänkirjautunut joukkue
            session['valittu'] = {
                'kilpailu': kilpailu_id,
                'sarja': None,
                'joukkue': joukkue['id']
            }

            # ohjataan sisäänkirjautumisen jälkeen joukkuelistaukseen
            return redirect(url_for('joukkueet.listaa'))

        except (AuthenticationError):
            # näytetään käyttäjälle virheilmoitus jos joukkuetta ei löydy tai salasana on väärä
            loginerrors.append('Kirjautuminen epäonnistui')
        
    # näytetään kirjautumissivu
    return render_template('common/login.html', loginform=loginform, loginerrors=loginerrors, role='joukkue')



@bp.route('/admin/login', methods=['GET','POST'])
def admin_login():
    """Reitti, jonka kautta ylläpitäjät kirjautuvat sovellukseen"""

    # luodaan kirjautumislomake
    form = AdminLoginForm()

    loginerrors = []

    # tarkistetaan formi
    if form.validate_on_submit():
        try:
            # haetaan hyväksytyt adminin tunnukset asetuksista
            id = current_app.config['ADMIN_ID']
            pw_hash = current_app.config['ADMIN_PW_HASH']

            # tarkistetaan annettu salasana, funktio heittää AuthenticationError:n jos salasana on väärä
            tarkista_salasana(pw_hash, form.salasana.data, id)

            # tallennetaan käyttäjän tiedot sessioon
            session['kayttaja'] = {
                'id': id,
                'roolit': ['admin']
            }

            # tallennetaan sessioon tieto valinnoista
            session['valittu'] = {
                'kilpailu': None,
                'sarja': None,
                'joukkue': None
            }

            # ohjataan sisäänkirjautumisen jälkeen kilpailulistaukseen
            return redirect(url_for('admin.listaa_kilpailut'))

        except (AuthenticationError):
            # näytetään käyttäjälle virheilmoitus jos joukkuetta ei löydy tai salasana on väärä
            loginerrors.append('Kirjautuminen epäonnistui')
    
    # näytetään kirjautumissivu
    return render_template('common/login.html', loginform=form, loginerrors=loginerrors, body_class="bg-lightblue", role='admin')


@bp.route('/logout')
def logout():
    """ Reitti, jonka kautta käyttäjä kirjataan ulos """

    # poistetaan sessiosta tiedot käyttäjästä ja valinnoista
    session.pop('kayttaja', None)
    session.pop('valittu', None)
    return redirect('/')
