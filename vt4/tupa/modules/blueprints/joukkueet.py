from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.domain.joukkue import Joukkue
from tupa.modules.services.data.dataservice import hae_joukkue, hae_joukkueen_leimaukset, hae_kilpailu, hae_joukkue_nimella, hae_sarjat, hae_sarjat_ja_joukkueet, paivita_joukkue
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.auth import hashaa_salasana
from tupa.modules.helpers.forms import MuokkausForm


### Joukkueena kirjautuneelle käyttäjälle näkyvä reitit ###
bp = Blueprint('joukkueet', __name__, url_prefix='/joukkueet')

@bp.route('/listaa', methods=['GET'], strict_slashes=False)
@sallitut_roolit(['joukkue'])
def listaa():
    """ Reitti, jonka kautta listataan kaikki valitun kilpailun sarjat ja joukkueet """

    # haetaan sessiosta tiedot valitusta kilpailusta ja joukkueesta
    valittu = session.get('valittu')
    kilpailu_id = valittu.get('kilpailu')
    joukkue_id = valittu.get('joukkue')

    # haetaan joukkueen ja kilpailun kaikki tiedot nimen näyttämistä varten
    kilpailu = hae_kilpailu(kilpailu_id)
    joukkue = hae_joukkue(joukkue_id)

    # haetaan kaikki kilpailun sarjat ja joukkueet, tiedot palautetaan monitasoisessa dictionaryssa
    sarjat_ja_joukkueet = hae_sarjat_ja_joukkueet(kilpailu_id=kilpailu_id)

    # näytetään listaussivu
    return render_template('joukkueet/lista.html', sarjat=sarjat_ja_joukkueet, kilpailu=kilpailu, joukkue=joukkue)



@bp.route('/muokkaa', methods=['GET', 'POST'], strict_slashes=False)
@sallitut_roolit(['joukkue'])
def muokkaa():
    """ Valitun joukkueen tietojen muokkaukseen käytettävä sivu """

    # haetaan sessiosta tiedot valitusta kilpailusta ja joukkueesta
    valittu = session.get('valittu')
    kilpailu_id = valittu.get('kilpailu')
    joukkue_id = valittu.get('joukkue')

    # haetaan joukkueen ja kilpailun kaikki tiedot
    kilpailu = hae_kilpailu(kilpailu_id)
    joukkue_dict = hae_joukkue(joukkue_id)

    # haetaan kaikki kilpailun sarjat tietokannasta ja muokataan tupleiksi
    sarjat = hae_sarjat(kilpailu_id)
    sarja_tuplet = [(sarja['id'], sarja['nimi']) for sarja in sarjat.values()]

    # luodaan muokkauslomake ja lisätään haetut sarjat vaihtoehdoiksi
    form = MuokkausForm()
    form.sarja.choices = sarja_tuplet

    # haetaan joukkueen leimaukset
    leimaukset = hae_joukkueen_leimaukset(joukkue_id)

    # jos sivu ladataan ensimmäistä kertaa, täytetään muokkauslomake valitun joukkueen tiedoilla
    if request.method == 'GET':

        # muunnetaan joukkue olioksi jotta ei tarvitse mapata kenttiä käsin
        joukkue = Joukkue(**joukkue_dict)
        form.process(obj=joukkue)

    # tarkistetaan lomake
    if form.validate_on_submit():
        toinen = hae_joukkue_nimella(kilpailu_id, form.nimi.data)

        if toinen:
            form.nimi.errors.append("Joukkue on jo olemassa!")
        else:
            # koostetaan lomakkeen tiedot dictionaryyn
            joukkue = {
                'id': joukkue_id,
                'nimi': form.nimi.data,
                # salasana päivitetään vain jos sitä on muokattu, muuten käytetään vanhaa salasanaa (nyt voidaan käyttää samaa querya)
                'salasana': hashaa_salasana(int(joukkue_id), form.salasana.data) if form.salasana.data != "" else joukkue_dict.get('salasana'),
                'sarja': form.sarja.data,
                # poistetaan tyhjät jäsenkentät
                'jasenet': str([_field.data for _field in form.jasenet if _field.data != ""])
            }

            # päivitetään joukkueen tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
            paivita_joukkue(joukkue)
            return redirect(url_for('joukkueet.listaa'))

    # näytetään joukkueen muokkaussivu
    # (samaa pohjaa käytetään monessa yhteydessä, sivun sisältö määritetään roolin ja moodin perusteella)
    return render_template('joukkueet/muokkaa.html',
                            form=form,
                            leimaukset=leimaukset,
                            kilpailu=kilpailu,
                            joukkue=joukkue_dict,
                            mode='edit',
                            role='joukkue',
                            action_url=url_for('joukkueet.muokkaa'))
