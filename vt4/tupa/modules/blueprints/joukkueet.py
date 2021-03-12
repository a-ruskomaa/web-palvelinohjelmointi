from collections import namedtuple
import pprint
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.services.data import ds
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import LisaysForm, MuokkausForm

pp = pprint.PrettyPrinter(indent=2)

bp = Blueprint('joukkueet', __name__, url_prefix='/joukkueet')


@bp.route('/listaa', methods=['GET', 'POST'])
@sallitut_roolit(['perus', 'admin'])
def listaa():
    """ Reitti, jonka kautta listataan kaikki valitun kilpailun sarjat ja joukkueet """

    kilpailut = _hae_kaikki_tiedot()
    kayttaja = session.get('kayttaja')
    print(kayttaja)

    valittu = {
        'kilpailu': None,
        'sarja': None,
        'joukkue': None
    }

    session['valittu'] = valittu

    # näytetään listaussivu
    return render_template('joukkueet/lista.html',
                            kilpailut=kilpailut,
                            roles=kayttaja['roolit'])



@bp.route('/lisaa', methods=['GET', 'POST'])
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

    if request.method == 'GET':
        if not form.sarja.data or form.sarja.data not in kilpailut[form.kilpailu.data]['sarjat'].keys():
            form.sarja.data = arr_sarjat[0][0] if len(arr_sarjat) > 0 else None


    # tarkistetaan lomake
    if form.validate_on_submit():
        kilpailu_id = int(form.kilpailu.data)
        sarja_id = int(form.sarja.data)

        # koostetaan lomakkeen tiedot dictionaryyn
        joukkue = {
            'nimi': form.nimi.data,
            # poistetaan tyhjät jäsenkentät
            'jasenet': [_field.data for _field in form.jasenet if _field.data != ""],
            'lisaaja': kayttaja.get('email')
        }

        # päivitetään joukkueen tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
        ds.lisaa_joukkue(joukkue, sarja_id, kilpailu_id)
        return redirect(url_for('joukkueet.listaa'))

    # näytetään joukkueen muokkaussivu
    # (samaa pohjaa käytetään monessa yhteydessä, sivun sisältö määritetään roolin ja moodin perusteella)
    return render_template('joukkueet/form.html',
                            form=form,
                            mode='lisaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('joukkueet.lisaa'))



@bp.route('/muokkaa', methods=['GET', 'POST'])
@sallitut_roolit(['perus', 'admin'])
def muokkaa():
    """ Valitun joukkueen tietojen muokkaukseen käytettävä sivu """

    kayttaja = session.get('kayttaja')
    valittu_kilpailu = session.get('kilpailu')

    joukkue_id = request.args.get('id', request.form.get('id', type=int), type=int)
    print(joukkue_id)
    vanha_sarja_id = request.args.get('sarja', request.form.get('vanha_sarja', type=int), type=int)
    print(vanha_sarja_id)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)
    print(kilpailu_id)

    joukkue = ds.hae_joukkue(joukkue_id, vanha_sarja_id, kilpailu_id)
    kilpailu = ds.hae_kilpailu(kilpailu_id)

    if not (joukkue and kilpailu):
        return render_template('error.html', message="Virheellinen tunniste")

    if (kayttaja['email'] != joukkue['lisaaja'] and
        not ('admin' in kayttaja['roolit'] and kilpailu_id == int(valittu_kilpailu))):
        print(f"kayttaja: {kayttaja}, lisaaja: {joukkue['lisaaja']}")
        print(kilpailu_id, int(valittu_kilpailu))
        return redirect(url_for('joukkueet.listaa'))

    if request.method == 'GET':
            Joukkue = namedtuple('Joukkue', ['id', 'vanha_sarja', 'sarja', 'kilpailu', 'nimi', 'jasenet'])
            joukkue_obj = Joukkue(joukkue_id, vanha_sarja_id, vanha_sarja_id, kilpailu_id, joukkue['nimi'], joukkue['jasenet'])
            print(joukkue_obj)
            form = MuokkausForm(obj=joukkue_obj)
    else:
        form = MuokkausForm()
    
    arr_sarjat = [(sarja.key.id, sarja['nimi']) for sarja in ds.hae_sarjat(kilpailu_id)]
    form.sarja.choices = arr_sarjat

    if not form.sarja.data:
        form.sarja.data = arr_sarjat[0][0]


    # tarkistetaan lomake
    if form.validate_on_submit():

        if form.poista.data:
            ds.poista_joukkue(joukkue_id, vanha_sarja_id, kilpailu_id)
            return redirect(url_for('joukkueet.listaa'))

        # koostetaan lomakkeen tiedot dictionaryyn
        joukkue_dict = {
            'nimi': form.nimi.data,
            # poistetaan tyhjät jäsenkentät
            'jasenet': [_field.data for _field in form.jasenet if _field.data != ""]
        }

        # päivitetään joukkueen tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
        sarja_id = form.sarja.data
        if vanha_sarja_id == sarja_id:
            ds.paivita_joukkue(joukkue_dict, joukkue_id, vanha_sarja_id, kilpailu_id)
        else:
            ds.poista_joukkue(joukkue_id, vanha_sarja_id, kilpailu_id)
            joukkue_dict['lisaaja'] = joukkue['lisaaja']
            ds.lisaa_joukkue(joukkue_dict, sarja_id, kilpailu_id)
        
        return redirect(url_for('joukkueet.listaa'))

    # näytetään joukkueen muokkaussivu
    # (samaa pohjaa käytetään monessa yhteydessä, sivun sisältö määritetään roolin ja moodin perusteella)
    return render_template('joukkueet/form.html',
                            form=form,
                            mode='muokkaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('joukkueet.muokkaa'))


######### APUFUNKTIOT ############

def _hae_kaikki_tiedot() -> dict:
    kilpailut = ds.hae_kilpailut()
    sarjat = ds.hae_sarjat()
    rastit = ds.hae_rastit()
    joukkueet = ds.hae_joukkueet()
    leimaukset = ds.hae_leimaukset()

    kayttaja = session.get('kayttaja')
    valittu_kilpailu = session.get('kilpailu')

    dict_kilpailut = {kilpailu.id:{key:kilpailu[key] for key in kilpailu.keys()} for kilpailu in kilpailut}

    for kilpailu_id, kilpailu in dict_kilpailut.items():
        kilpailu['sarjat'] = {sarja.id:{key:sarja[key] for key in sarja.keys()} for sarja in sarjat if sarja.key.parent.id == kilpailu_id}
        kilpailu['rastit'] = {rasti.id:{key:rasti[key] for key in rasti.keys()} for rasti in rastit if rasti.key.parent.id == kilpailu_id}

        for rasti in kilpailu['rastit'].values():
            rasti['saa_muokata'] = ('admin' in kayttaja['roolit'] and kilpailu_id == valittu_kilpailu)

        for sarja_id, sarja in kilpailu['sarjat'].items():
            sarja['joukkueet'] = {joukkue.id:{key:joukkue[key] for key in joukkue.keys()} for joukkue in joukkueet if joukkue.key.parent.id == sarja_id}
            for joukkue_id, joukkue in sarja['joukkueet'].items():
                joukkue['saa_muokata'] = ('admin' in kayttaja['roolit'] and kilpailu_id == valittu_kilpailu
                                        or joukkue['lisaaja'] == kayttaja['email'])
                joukkue['leimaukset'] = {leimaus.id:{key:leimaus[key] for key in leimaus.keys()} for leimaus in leimaukset if leimaus.key.parent.id == joukkue_id}

    return dict_kilpailut