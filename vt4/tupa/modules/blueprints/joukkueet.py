import pprint
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.domain.joukkue import Joukkue
from tupa.modules.services.data.dataservice import hae_joukkue, hae_joukkueet, hae_sarjat, hae_kilpailut, lisaa_joukkue, paivita_joukkue
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import LisaysForm, MuokkausForm

pp = pprint.PrettyPrinter(indent=2)


### Joukkueena kirjautuneelle käyttäjälle näkyvä reitit ###
bp = Blueprint('joukkueet', __name__, url_prefix='/joukkueet')

@bp.route('/listaa', methods=['GET', 'POST'], strict_slashes=False)
@sallitut_roolit(['perus', 'admin'])
def listaa():
    """ Reitti, jonka kautta listataan kaikki valitun kilpailun sarjat ja joukkueet """

    kilpailut = _hae_kaikki_tiedot()

    valittu = {
        'kilpailu': None,
        'joukkue': None
    }

    session['valittu'] = valittu

    # näytetään listaussivu
    return render_template('joukkueet/lista.html', kilpailut=kilpailut)



@bp.route('/lisaa', methods=['GET', 'POST'], strict_slashes=False)
@sallitut_roolit(['perus', 'admin'])
def lisaa():
    """ Uuden joukkueen lisäämiseen käytettävä sivu """

    kayttaja = session.get('kayttaja')
    kilpailut = _hae_kaikki_tiedot()

    if request.method == 'GET':
        form = LisaysForm(request.args)
    else:
        form = LisaysForm()

    arr_kilpailut = [(id, kilpailu['nimi']) for id, kilpailu in kilpailut.items()]
    form.kilpailu.choices = arr_kilpailut

    if not form.kilpailu.data:
        form.kilpailu.data = arr_kilpailut[0][0]
    
    arr_sarjat = [(id, sarja['nimi']) for id, sarja in kilpailut[form.kilpailu.data]['sarjat'].items()]
    form.sarja.choices = arr_sarjat

    if not form.sarja.data or form.sarja.data not in kilpailut[form.kilpailu.data]['sarjat'].keys():
        form.sarja.data = arr_sarjat[0][0] if len(arr_sarjat) > 0 else None


    # tarkistetaan lomake
    if form.validate_on_submit():
        kilpailu_id = int(form.kilpailu.data)

        toinen = False

        for sarja in kilpailut[kilpailu_id]['sarjat'].values():
            for joukkue in sarja['joukkueet'].values():
                if joukkue['nimi'] == form.nimi.data:
                    toinen = True

        if toinen:
            form.nimi.errors.append("Joukkue on jo olemassa!")
        else:
            # koostetaan lomakkeen tiedot dictionaryyn
            joukkue = {
                'nimi': form.nimi.data,
                # poistetaan tyhjät jäsenkentät
                'jasenet': [_field.data for _field in form.jasenet if _field.data != ""],
                'omistaja': kayttaja.get('email')
            }

            # päivitetään joukkueen tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
            lisaa_joukkue(joukkue, parent_id=int(form.sarja.data))
            return redirect(url_for('joukkueet.listaa'))

    # näytetään joukkueen muokkaussivu
    # (samaa pohjaa käytetään monessa yhteydessä, sivun sisältö määritetään roolin ja moodin perusteella)
    return render_template('joukkueet/form.html',
                            form=form,
                            mode='lisaa',
                            role='perus',
                            action_url=url_for('joukkueet.lisaa'))



@bp.route('/muokkaa', methods=['GET', 'POST'], strict_slashes=False)
@sallitut_roolit(['perus', 'admin'])
def muokkaa():
    """ Valitun joukkueen tietojen muokkaukseen käytettävä sivu """

    kayttaja = session.get('kayttaja')
    kilpailut = _hae_kaikki_tiedot()


    if request.method == 'GET':
        joukkue_id = request.args.get('id')
        if joukkue_id:
            joukkue = hae_joukkue(joukkue_id=joukkue_id)
        form = MuokkausForm(obj=joukkue)
    else:
        form = MuokkausForm()

    arr_kilpailut = [(id, kilpailu['nimi']) for id, kilpailu in kilpailut.items()]
    form.kilpailu.choices = arr_kilpailut

    if not form.kilpailu.data:
        form.kilpailu.data = arr_kilpailut[0][0]
    
    arr_sarjat = [(id, sarja['nimi']) for id, sarja in kilpailut[form.kilpailu.data]['sarjat'].items()]
    form.sarja.choices = arr_sarjat

    if not form.sarja.data or form.sarja.data not in kilpailut[form.kilpailu.data]['sarjat'].keys():
        form.sarja.data = arr_sarjat[0][0] if len(arr_sarjat) > 0 else None


    # tarkistetaan lomake
    if form.validate_on_submit():
        kilpailu_id = int(form.kilpailu.data)

        toinen = False

        for sarja in kilpailut[kilpailu_id]['sarjat'].values():
            for joukkue in sarja['joukkueet'].values():
                if joukkue['nimi'] == form.nimi.data:
                    toinen = True

        if toinen:
            form.nimi.errors.append("Joukkue on jo olemassa!")
        else:
            # koostetaan lomakkeen tiedot dictionaryyn
            joukkue = {
                'nimi': form.nimi.data,
                # poistetaan tyhjät jäsenkentät
                'jasenet': [_field.data for _field in form.jasenet if _field.data != ""],
                'omistaja': kayttaja.get('email')
            }

            # päivitetään joukkueen tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
            paivita_joukkue(joukkue, parent_id=int(form.sarja.data))
            return redirect(url_for('joukkueet.listaa'))

    # näytetään joukkueen muokkaussivu
    # (samaa pohjaa käytetään monessa yhteydessä, sivun sisältö määritetään roolin ja moodin perusteella)
    return render_template('joukkueet/form.html',
                            form=form,
                            mode='muokkaa',
                            role='perus',
                            action_url=url_for('joukkueet.muokkaa'))


######### APUFUNKTIOT ############
def _hae_kaikki_tiedot() -> dict:
    kilpailut = hae_kilpailut()
    sarjat = hae_sarjat()
    joukkueet = hae_joukkueet()

    kayttaja = session.get('kayttaja')
    for joukkue in joukkueet:
        if 'admin' in kayttaja['roolit'] or joukkue['omistaja'] == kayttaja['email']:
            joukkue['saa_muokata'] = True

    dict_kilpailut = {kilpailu.id:{key:kilpailu[key] for key in kilpailu.keys()} for kilpailu in kilpailut}

    for id, kilpailu in dict_kilpailut.items():
        kilpailu['sarjat'] = {sarja.id:{key:sarja[key] for key in sarja.keys()} for sarja in sarjat if sarja.key.parent.id == id}

        for id, sarja in kilpailu['sarjat'].items():
            sarja['joukkueet'] = {joukkue.id:{key:joukkue[key] for key in joukkue.keys()} for joukkue in joukkueet if joukkue.key.parent.id == id}

    return dict_kilpailut