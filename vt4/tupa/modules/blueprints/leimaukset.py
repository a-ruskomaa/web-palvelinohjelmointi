from collections import namedtuple
from datetime import datetime
import pprint
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.services.data import ds
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import LeimausForm, LisaysForm, MuokkausForm

bp = Blueprint('leimaukset', __name__, url_prefix='/leimaukset')

Leimaus = namedtuple('Leimaus', ['id', 'joukkue', 'kilpailu', 'aika', 'rasti'])

@bp.route('/lisaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def lisaa():
    """ Leimauksen muokkaukseen käytettävä sivu """
    
    # haetaan valitun kilpailun tiedot sessiosta
    valittu_kilpailu = session.get('kilpailu')
    kayttaja = session.get('kayttaja')

    joukkue_id = request.args.get('joukkue', request.form.get('joukkue', type=int), type=int)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)

    kilpailu = ds.hae_kilpailu(kilpailu_id)

    if not (kilpailu):
        return render_template('error.html', message="Virheellinen tunniste")

    if kilpailu_id != int(valittu_kilpailu):
        return redirect(url_for('joukkueet.listaa'))

    # jos sivu ladataan ensimmäistä kertaa, täytetään lomakkeen tiedot valmiiksi
    if request.method == 'GET':
        leimaus_obj = Leimaus(None, joukkue_id, kilpailu_id, None, None)

        form = LeimausForm(obj=leimaus_obj)
    else:
        # luodaan muokkauslomake
        form = LeimausForm()

    # haetaan kilpailun rastit ja lisätään lomakkeelle vaihtoehdoiksi
    rastit = ds.hae_rastit(kilpailu_id=kilpailu_id)
    rastituplet = [(rasti.key.id, rasti['koodi']) for rasti in rastit]
    form.rasti.choices = rastituplet

    # jos POST-pyyntö ja lomake validi
    if form.validate_on_submit():

        # haetaan päivitetyt tiedot lomakkeelta ja päivitetään kanta
        leimaus_dict = {
            'aika': form.aika.data,
            'rasti': form.rasti.data
        }
        ds.lisaa_leimaus(leimaus=leimaus_dict, joukkue_id=joukkue_id, kilpailu_id=kilpailu_id)

        # uudelleenohjataan joukkueen muokkaussivulle
        return redirect(url_for('joukkueet.listaa'))


    return render_template('leimaukset/form.html',
                            form=form,
                            mode='lisaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('leimaukset.lisaa'))


@bp.route('/muokkaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def muokkaa():
    """ Leimauksen muokkaukseen käytettävä sivu """
    
    # haetaan valitun kilpailun tiedot sessiosta
    valittu_kilpailu = session.get('kilpailu')
    kayttaja = session.get('kayttaja')

    # haetaan leimauksen tiedot joko pyynnön parametreista tai lomakkeelta
    leimaus_id = request.args.get('id', request.form.get('id', type=int), type=int)
    joukkue_id = request.args.get('joukkue', request.form.get('joukkue', type=int), type=int)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)
    # aika = request.args.get('aika', request.form.get('vanha_aika', type=datetime.fromisoformat), type=datetime.fromisoformat)
    # rasti = request.args.get('rasti', request.form.get('vanha_rasti'))

    leimaus = ds.hae_leimaus(leimaus_id=leimaus_id, joukkue_id=joukkue_id, kilpailu_id=kilpailu_id)
    kilpailu = ds.hae_kilpailu(kilpailu_id)

    if not (leimaus and kilpailu):
        return render_template('error.html', message="Virheellinen tunniste")

    if kilpailu_id != int(valittu_kilpailu):
        return redirect(url_for('joukkueet.listaa'))

    # jos sivu ladataan ensimmäistä kertaa, täytetään lomakkeen tiedot valmiiksi
    if request.method == 'GET':
        Leimaus = namedtuple('Leimaus', ['id', 'joukkue', 'kilpailu', 'aika', 'rasti'])
        leimaus_obj = Leimaus(leimaus_id, joukkue_id, kilpailu_id, leimaus['aika'], leimaus['rasti'])

        form = LeimausForm(obj=leimaus_obj)
    else:
        # luodaan muokkauslomake
        form = LeimausForm()

    # haetaan kilpailun rastit ja lisätään lomakkeelle vaihtoehdoiksi
    rastit = ds.hae_rastit(kilpailu_id=kilpailu_id)
    rastituplet = [(rasti.key.id, rasti['koodi']) for rasti in rastit]
    form.rasti.choices = rastituplet

    # jos POST-pyyntö ja lomake validi
    if form.validate_on_submit():

        if form.poista.data:
            # poistetaan leimaus jos poistokenttä on valittuna
            ds.poista_leimaus(leimaus_id=leimaus_id, joukkue_id=joukkue_id, kilpailu_id= kilpailu_id)
        else:
            # haetaan päivitetyt tiedot lomakkeelta ja päivitetään kanta
            leimaus_dict = {
                'aika': form.aika.data,
                'rasti': form.rasti.data
            }
            ds.paivita_leimaus(leimaus=leimaus_dict, leimaus_id=leimaus_id, joukkue_id=joukkue_id, kilpailu_id=kilpailu_id)

        # uudelleenohjataan joukkueen muokkaussivulle
        return redirect(url_for('joukkueet.listaa'))


    return render_template('leimaukset/form.html',
                            form=form,
                            mode='muokkaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('leimaukset.muokkaa'))