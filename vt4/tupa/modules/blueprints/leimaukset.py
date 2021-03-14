from collections import namedtuple
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.services.data import ds
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import LeimausForm

bp = Blueprint('leimaukset', __name__, url_prefix='/leimaukset')

Leimaus = namedtuple('Leimaus', ['id', 'joukkue', 'sarja', 'kilpailu', 'aika', 'rasti'])

@bp.route('/lisaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def lisaa():
    """ Leimauksen muokkaukseen käytettävä sivu """
    
    # haetaan valitun kilpailun tiedot sessiosta
    valittu_kilpailu = session.get('kilpailu')
    kayttaja = session.get('kayttaja')

    # haetaan kaikki muokattavaan leimaukseen liittyvä tiedot
    joukkue_id = request.args.get('joukkue', request.form.get('joukkue', type=int), type=int)
    sarja_id = request.args.get('sarja', request.form.get('sarja', type=int), type=int)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)

    kilpailu = ds.hae_kilpailu(kilpailu_id)
    joukkue = ds.hae_joukkue(joukkue_id=joukkue_id, sarja_id=sarja_id, kilpailu_id=kilpailu_id)

    # varmistetaan että tietoja vastaava joukkue ja kilpailu löytyvät tietokannasta
    if not (kilpailu and joukkue):
        return render_template('error.html', message="Virheellinen tunniste")

    # varmistetaan että parametrina annettu kilpailu vastaa valittua
    if kilpailu_id != int(valittu_kilpailu):
        return redirect(url_for('joukkueet.listaa'))

    # luodaan lomake täytettynä muokattavan joukkueen ja kilpailun tiedoilla
    leimaus_obj = Leimaus(None, joukkue_id, sarja_id, kilpailu_id, None, None)
    form = LeimausForm(obj=leimaus_obj)
    
    # haetaan kilpailun rastit ja lisätään lomakkeelle vaihtoehdoiksi
    rastit = ds.hae_rastit(kilpailu_id=kilpailu_id)
    rastituplet = [(rasti.key.id, rasti['koodi']) for rasti in rastit]
    form.rasti.choices = rastituplet

    # tarkistetaan lomake
    if form.validate_on_submit():

        # haetaan päivitetyt tiedot lomakkeelta ja päivitetään kanta
        leimaus_dict = {
            form.rasti.data: form.aika.data
        }

        joukkue['leimaukset'].update(leimaus_dict)

        ds.paivita_joukkue(joukkue=joukkue, joukkue_id=joukkue_id, sarja_id=sarja_id, kilpailu_id=kilpailu_id)

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
    leimaus_id = request.args.get('id', request.form.get('id', type=str), type=str) # vanha rasti
    joukkue_id = request.args.get('joukkue', request.form.get('joukkue', type=int), type=int)
    sarja_id = request.args.get('sarja', request.form.get('sarja', type=int), type=int)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)

    kilpailu = ds.hae_kilpailu(kilpailu_id)
    joukkue = ds.hae_joukkue(joukkue_id=joukkue_id, sarja_id=sarja_id, kilpailu_id=kilpailu_id)

    # varmistetaan että tietoja vastaava joukkue ja kilpailu löytyvät tietokannasta
    if not (kilpailu and joukkue):
        return render_template('error.html', message="Virheellinen tunniste")

    # varmistetaan että parametrina annettu kilpailu vastaa valittua
    if kilpailu_id != int(valittu_kilpailu):
        return redirect(url_for('joukkueet.listaa'))

    # haetaan muokattavan leimauksen tiedot
    try:
        vanhat_leimaukset = joukkue.get('leimaukset', {})
        leimaus = vanhat_leimaukset.get(leimaus_id)
    except KeyError:
        return render_template('error.html', message="Virheellinen tunniste")


    # luodaan lomake täytettynä valitun leimauksen tiedoilla
    leimaus_obj = Leimaus(leimaus_id, joukkue_id, sarja_id, kilpailu_id, leimaus, leimaus_id)
    form = LeimausForm(obj=leimaus_obj)

    # haetaan kilpailun rastit ja lisätään lomakkeelle vaihtoehdoiksi
    rastit = ds.hae_rastit(kilpailu_id=kilpailu_id)
    rastituplet = [(rasti.key.id, rasti['koodi']) for rasti in rastit]
    form.rasti.choices = rastituplet

    # jos POST-pyyntö ja lomake validi
    if form.validate_on_submit():

        if form.poista.data:
            # poistetaan leimaus jos poistokenttä on valittuna
            leimaukset = {k: v for k,v in vanhat_leimaukset.items() if k != leimaus_id}
            joukkue['leimaukset'] = leimaukset

        else:
            # haetaan päivitetyt tiedot lomakkeelta ja päivitetään kanta
            leimaus_dict = {
                form.rasti.data: form.aika.data
            }

            # poistetaan aiempi leimaus siltä varalta, että leimattu rasti on vaihdettu
            leimaukset = {k: v for k,v in vanhat_leimaukset.items() if k != leimaus_id}
            leimaukset.update(leimaus_dict)
            joukkue['leimaukset'] = leimaukset

        ds.paivita_joukkue(joukkue=joukkue, joukkue_id=joukkue_id, sarja_id=sarja_id, kilpailu_id=kilpailu_id)

        # uudelleenohjataan joukkueen muokkaussivulle
        return redirect(url_for('joukkueet.listaa'))


    return render_template('leimaukset/form.html',
                            form=form,
                            mode='muokkaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('leimaukset.muokkaa'))