from collections import namedtuple
from datetime import datetime, tzinfo
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.services.data import ds
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import LisaysForm, MuokkausForm

bp = Blueprint('joukkueet', __name__, url_prefix='/joukkueet')

Joukkue = namedtuple('Joukkue', ['id', 'vanha_sarja', 'sarja', 'kilpailu', 'nimi', 'jasenet'])

@bp.route('/listaa', methods=['GET', 'POST'])
@sallitut_roolit(['perus', 'admin'])
def listaa():
    """ Reitti, jonka kautta listataan kaikkien kilpailujen tiedot """

    # apufunktio, jota käytetään hakemaan rastileimausta vastaava koodi
    def koodinhakija(kilpailut):
        """ Palauttaa funktion, joka hakee kilpailun ja rastin id:n perusteella rastin koodin. """
        def _hae_koodi(kilpailu_id, rasti_id) -> str:
            # haetaan rastin tiedot kilpailusta
            rasti = kilpailut[kilpailu_id]['rastit'].get(rasti_id)

            return rasti['koodi'] if rasti else "Tuntematon"
        return _hae_koodi

    kilpailut = _hae_kaikki_tiedot()

    # näytetään listaussivu
    return render_template('joukkueet/lista.html',
                            kilpailut=kilpailut,
                            hae_koodi = koodinhakija(kilpailut))



@bp.route('/lisaa', methods=['GET', 'POST'])
@sallitut_roolit(['perus', 'admin'])
def lisaa():
    """ Uuden joukkueen lisäämiseen käytettävä sivu """

    kayttaja = session.get('kayttaja')
    kilpailut = _hae_kaikki_tiedot()

    # jos kilpailuja ei ole, ei uutta joukkuetta voida lisätä
    if len(kilpailut) == 0:
        return redirect(url_for('joukkueet.listaa'))

    if request.method == 'GET':
        # täytetään lomakkeen tiedot get pyynnön parametreilla jos ollaan vaihtamassa valittua kilpailua
        form = LisaysForm(request.args)
    else:
        form = LisaysForm()

    # lisätään haetut kilpailut vaihtoehdoiksi
    arr_kilpailut = [(id, kilpailu['nimi']) for id, kilpailu in kilpailut.items()]
    form.kilpailu.choices = arr_kilpailut

    # valitaan tarvittaessa ensimmäinen kilpailu valmiiksi
    if not form.kilpailu.data:
        form.kilpailu.data = arr_kilpailut[0][0] if len(arr_kilpailut) > 0 else None
    
    # lisätään kilpailuun kuuluvat sarjat vaihtoehdoiksi
    arr_sarjat = [(id, sarja['nimi']) for id, sarja in kilpailut[form.kilpailu.data]['sarjat'].items()]
    form.sarja.choices = arr_sarjat

    # valitaan tarvittaessa ensimmäinen kilpailun sarja valmiiksi
    # tämä tehdään vain get-metodille, jotta lomaketta lähetettäessä sarjaa ei talleneta vahingossa
    # väärään sarjaan jos käyttäjä onkin vaihtanut kilpailua ennen lomakkeen lähettämistä
    if request.method == 'GET':
        if not form.sarja.data or form.sarja.data not in kilpailut[form.kilpailu.data]['sarjat'].keys():
            form.sarja.data = arr_sarjat[0][0] if len(arr_sarjat) > 0 else None


    # tarkistetaan lomake
    if form.validate_on_submit():
        kilpailu_id = int(form.kilpailu.data)
        sarja_id = int(form.sarja.data)

        # koostetaan lomakkeen tiedot dictionaryyn
        joukkue_dict = {
            'nimi': form.nimi.data,
            # poistetaan tyhjät jäsenkentät ja järjestetään jäsenet ennen lisäämistä
            'jasenet': sorted([_field.data for _field in form.jasenet if _field.data != ""]),
            'leimaukset': {},
            'lisaaja': kayttaja.get('email')
        }

        # lisätään joukkueen tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
        ds.lisaa_joukkue(joukkue_dict, sarja_id, kilpailu_id)
        return redirect(url_for('joukkueet.listaa'))

    # näytetään joukkueen lisäys/muokkauslomake lisäystilassa
    return render_template('joukkueet/form.html',
                            form=form,
                            mode='lisaa',
                            action_url=url_for('joukkueet.lisaa'))



@bp.route('/muokkaa', methods=['GET', 'POST'])
@sallitut_roolit(['perus', 'admin'])
def muokkaa():
    """ Valitun joukkueen muokkaukseen käytettävä sivu """

    kayttaja = session.get('kayttaja')
    valittu_kilpailu = session.get('kilpailu')

    # haetaan muokattavan joukkueen tiedot joko pyynnön parametreista tai lomakkeelta
    joukkue_id = request.args.get('id', request.form.get('id', type=int), type=int)
    vanha_sarja_id = request.args.get('sarja', request.form.get('vanha_sarja', type=int), type=int)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)

    joukkue = ds.hae_joukkue(joukkue_id, vanha_sarja_id, kilpailu_id)
    kilpailu = ds.hae_kilpailu(kilpailu_id)

    # varmistetaan että tietoja vastaava joukkue ja kilpailu löytyvät tietokannasta
    if not (joukkue and kilpailu):
        return render_template('error.html', message="Virheellinen tunniste")

    # varmistetaan että käyttäjällä on oikeus muokata joukkuetta
    if (kayttaja['email'] != joukkue['lisaaja'] and
        not ('admin' in kayttaja['roolit'] and kilpailu_id == int(valittu_kilpailu))):
        return redirect(url_for('joukkueet.listaa'))

    # luodaan lomake täytettynä valitun joukkueen tiedoilla
    joukkue_obj = Joukkue(joukkue_id, vanha_sarja_id, vanha_sarja_id, kilpailu_id, joukkue['nimi'], joukkue['jasenet'])
    form = MuokkausForm(obj=joukkue_obj)
    
    # haetaan kilpailun sarjat
    arr_sarjat = [(sarja.key.id, sarja['nimi']) for sarja in ds.hae_sarjat(kilpailu_id)]
    form.sarja.choices = arr_sarjat

    # valitaan ensimmäinen sarja jos mitään ei ole vielä valittuna
    if not form.sarja.data:
        form.sarja.data = arr_sarjat[0][0] if len(arr_sarjat) > 0 else None

    # tarkistetaan lomake
    if form.validate_on_submit():

        # jos joukkue on valittu poistettavaksi, 
        if form.poista.data:
            ds.poista_joukkue(joukkue_id, vanha_sarja_id, kilpailu_id)
            return redirect(url_for('joukkueet.listaa'))

        # koostetaan lomakkeen tiedot dictionaryyn
        joukkue_dict = {
            'nimi': form.nimi.data,
            # poistetaan tyhjät jäsenkentät ja järjestetään jäsenten tiedot
            'jasenet': sorted([_field.data for _field in form.jasenet if _field.data != ""])
        }

        # päivitetään joukkueen tiedot kantaan ja uudelleenohjataan takaisin joukkuelistaukseen
        sarja_id = form.sarja.data
        if vanha_sarja_id == sarja_id:
            # jos sarja ei ole vaihtunut, tehdään päivitys suoraan
            ds.paivita_joukkue(joukkue_dict, joukkue_id, vanha_sarja_id, kilpailu_id)
        else:
            # jos sarja on vaihdettu, pitää joukkueen avain luoda uusiksi, joka tehdään poistamalla joukkue ja lisäämällä uusi
            # nyt joukkueen id vaihtuu, joka voi rikkoa toiminallisuutta jos esim. leimauksen avaimessa on joukkueen id...
            # nykyisellä toteutustavalla tällä ei kuitenkaan ole merkitystä
            ds.poista_joukkue(joukkue_id, vanha_sarja_id, kilpailu_id)
            joukkue_dict['lisaaja'] = joukkue['lisaaja']
            joukkue_dict['leimaukset'] = joukkue['leimaukset']
            ds.lisaa_joukkue(joukkue_dict, sarja_id, kilpailu_id)
        
        return redirect(url_for('joukkueet.listaa'))

    # näytetään joukkueen muokkaussivu
    # (samaa pohjaa käytetään monessa yhteydessä, sivun sisältö määritetään roolin ja moodin perusteella)
    return render_template('joukkueet/form.html',
                            form=form,
                            mode='muokkaa',
                            action_url=url_for('joukkueet.muokkaa'))


######### APUFUNKTIOT ############

def _hae_kaikki_tiedot() -> dict:
    # haetaan datastoresta kaikki entityt
    kilpailut = ds.hae_kilpailut()
    sarjat = ds.hae_sarjat()
    rastit = ds.hae_rastit()
    joukkueet = ds.hae_joukkueet()

    kayttaja = session.get('kayttaja')
    valittu_kilpailu = session.get('kilpailu')

    # lisätään kilpailut hakemistoon, jossa tiedot palautetaan
    dict_kilpailut = {kilpailu.id:{key:kilpailu[key] for key in kilpailu.keys()} for kilpailu in kilpailut}

    # iteroidaan kilpailut läpi ja lisätään niihin kuuluvat sarjat, rastit ja joukkueet alihakemistoina
    # ratkaisu ei ole järin tehokas, mutta aivan riittävä tälle datan määrälle ja mukavan suoraviivainen
    for kilpailu_id, kilpailu in dict_kilpailut.items():
        kilpailu['sarjat'] = {sarja.id:{key:sarja[key] for key in sarja.keys()} for sarja in sarjat if sarja.key.parent.id == kilpailu_id}
        kilpailu['rastit'] = {rasti.id:{key:rasti[key] for key in rasti.keys()} for rasti in rastit if rasti.key.parent.id == kilpailu_id}

        # tallennetaan valitun kilpailun rastien tietoihin lupa muokata, jos ollaan admin-tilassa
        for rasti in kilpailu['rastit'].values():
            rasti['saa_muokata'] = ('admin' in kayttaja['roolit'] and kilpailu_id == valittu_kilpailu)

        for sarja_id, sarja in kilpailu['sarjat'].items():
            # lisätään joukkueet sarjakohtaisesti
            sarja['joukkueet'] = {joukkue.id:{key:joukkue[key] for key in joukkue.keys()} for joukkue in joukkueet if joukkue.key.parent.id == sarja_id}
            for joukkue in sarja['joukkueet'].values():

                # tallennetaan joukkueiden tietoihin lupa muokata, jos ollaan oikean kilpailun admin-tilassa tai joukkueen lisääjä
                joukkue['saa_muokata'] = ('admin' in kayttaja['roolit'] and kilpailu_id == valittu_kilpailu
                                        or joukkue['lisaaja'] == kayttaja['email'])
                
                # muunnetaan helpompaa käsittelyä varten leimausten id kokonaisluvuksi ja aikaleima merkkijonoksi
                leimaukset = {int(key): value.strftime("%Y-%m-%d %H:%M:%S") for key, value in sorted(joukkue['leimaukset'].items(), key=lambda item: item[1])}
                joukkue['leimaukset'] = leimaukset
    
    return dict_kilpailut