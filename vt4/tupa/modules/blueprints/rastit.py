from collections import namedtuple
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.services import data
from tupa.modules.services.data import ds
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import RastiForm

Rasti = namedtuple('Rasti', ['id', 'kilpailu', 'koodi', 'lat', 'lon'])

bp = Blueprint('rastit', __name__, url_prefix='/rastit')

@bp.route('/lisaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def lisaa():
    """ Uuden rastin lisäämiseen käytettävä sivu """

    valittu_kilpailu = session.get('kilpailu')
    kayttaja = session.get('kayttaja')

    # luodaan lomake
    form = RastiForm(data={'kilpailu': valittu_kilpailu})

    if form.validate_on_submit():
        # koostetaan lomakkeen tiedot dictionaryyn
        rasti_dict = {
            'koodi': form.koodi.data,
            'lat': form.lat.data,
            'lon': form.lon.data
        }

        # tallennetaan uusi rasti tietokantaan
        ds.lisaa_rasti(rasti=rasti_dict, kilpailu_id=valittu_kilpailu)

        return redirect(url_for('joukkueet.listaa'))
    
    # näytetään rastin lisäys/muokkauslomake lisäystilassa
    return render_template('rastit/form.html',
                            form=form,
                            mode='lisaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('rastit.lisaa'))


@bp.route('/muokkaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def muokkaa():
    kayttaja = session.get('kayttaja')
    valittu_kilpailu = session.get('kilpailu')

    # haetaan muokattavan rastin tiedot joko pyynnön parametreista tai lomakkeelta
    rasti_id = request.args.get('id', request.form.get('id', type=int), type=int)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)

    rasti = ds.hae_rasti(rasti_id=rasti_id, kilpailu_id=kilpailu_id)
    kilpailu = ds.hae_kilpailu(kilpailu_id)
    
    # varmistetaan että tietoja vastaava rasti ja kilpailu löytyvät tietokannasta
    if not (rasti and kilpailu):
        return render_template('error.html', message="Virheellinen tunniste")

    # varmistetaan että käyttäjällä on oikeus muokata kilpailua
    if kilpailu_id != int(valittu_kilpailu):
        return redirect(url_for('joukkueet.listaa'))

    # luodaan lomake täytettynä valitun rastin tiedoilla
    rasti_obj = Rasti(rasti_id, kilpailu_id, rasti['koodi'], rasti['lat'], rasti['lon'])
    form = RastiForm(obj=rasti_obj)

    # tarkistetaan lomake
    if form.validate_on_submit():

        # jos rasti on valittu poistettavaksi
        if form.poista.data:
            ds.poista_rasti(rasti_id=rasti_id, kilpailu_id=kilpailu_id)
            return redirect(url_for('joukkueet.listaa'))
        
        # koostetaan rastin tiedot dictionaryyn
        rasti_dict = {
            'koodi': form.koodi.data,
            'lat': form.lat.data,
            'lon': form.lon.data
        }

        # päivitetään rastin tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
        ds.paivita_rasti(rasti_id=rasti_id, rasti=rasti_dict, kilpailu_id=valittu_kilpailu)
        return redirect(url_for('joukkueet.listaa'))

    # näytetään rastin lisäys/muokkauslomake muokkaustilassa
    return render_template('rastit/form.html',
                            form=form,
                            mode='muokkaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('rastit.muokkaa'))