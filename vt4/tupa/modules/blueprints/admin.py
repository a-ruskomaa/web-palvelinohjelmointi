from datetime import datetime
from flask import Blueprint, render_template
from flask import redirect, request, session
from flask.globals import session
from flask.helpers import url_for
from wtforms.validators import ValidationError
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.domain.joukkue import Joukkue
from tupa.modules.helpers.auth import hashaa_salasana
from tupa.modules.helpers.forms import LeimausForm, MuokkausForm, LisaysForm
from tupa.modules.data.dataservice import (hae_joukkue_nimella, hae_joukkueen_leimaukset,
                                            hae_kilpailun_rastit,
                                            hae_kilpailut,
                                            hae_sarjat,
                                            hae_joukkueet,
                                            hae_joukkue,
                                            paivita_joukkue,
                                            lisaa_joukkue,
                                            hae_kilpailun_rastit_ja_leimaukset,
                                            paivita_leimaus,
                                            poista_joukkue,
                                            poista_leimaus)


### Ylläpitäjänä kirjautuneelle käyttäjälle näkyvä reitit ###
bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/', methods=['GET'])
@sallitut_roolit(['admin'])
def index():
    """ "Etusivu", jolta uudelleenohjataan kilpailulistaukseen """
    return redirect(url_for('admin.listaa_kilpailut'))



@bp.route('/kilpailut', methods=['GET'])
@sallitut_roolit(['admin'])
def listaa_kilpailut():
    """ Reitti, jonka kautta listataan kaikki kilpailut """

    # haetaan kilpailut ja näytetään sivu
    kilpailut = hae_kilpailut()
    return render_template('admin/listaa_kilpailut.html', items=kilpailut, urlstring='admin.listaa_sarjat')



@bp.route('/sarjat', methods=['GET'])
@sallitut_roolit(['admin'])
def listaa_sarjat():
    """ Reitti, jonka kautta listataan kaikki valitun kilpailun sarjat """

    # haetaan valittu kilpailu, ensisijaisesti pyynnön parametreista, toissijaisesti sessiosta
    valittu_kilpailu = request.args.get('id', session.get('valittu').get('kilpailu'))

    # jos kilpailua ei ole valittu, ohjataan kilpailulistaukseen
    if not valittu_kilpailu:
        return redirect(url_for('admin.listaa_kilpailut'))

    # tallennetaan tieto valitusta kilpailusta sessioon
    session['valittu'] = {
        'kilpailu': valittu_kilpailu,
        'sarja': None,
        'joukkue': None
    }

    # haetaan sarjat ja näytetään sivu
    sarjat = hae_sarjat(kilpailu_id=valittu_kilpailu)
    return render_template('admin/listaa_sarjat.html', items=sarjat, urlstring='admin.listaa_joukkueet')



@bp.route('/joukkueet', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def listaa_joukkueet():
    """ Reitti, jonka kautta listataan kaikki valitun sarjan joukkueet """

    # turvonnut funktio, joka pitäisi pilkkoa pienemmiksi mutta ei jaksa...

    # haetaan valittu sarja, ensisijaisesti pyynnön parametreista, toissijaisesti sessiosta
    valittu_sarja = request.args.get('id', session.get('valittu').get('sarja'))
    valittu_kilpailu = session.get('valittu').get('kilpailu')

    # jos sarjaa ei ole valittu, ohjataan sarjalistaukseen
    if not valittu_sarja:
        return redirect(url_for('admin.listaa_sarjat'))

    # tallennetaan tieto valitusta sarjasta sessioon
    session['valittu'] = {
        'kilpailu': valittu_kilpailu,
        'sarja': valittu_sarja,
        'joukkue': None
    }

    # luodaan lomake uuden joukkueen lisäämistä varten
    form = LisaysForm()
    form.sarja.data = valittu_sarja
    
    viesti = None

    # tarkistetaan lomake jos POST-pyyntö
    if form.validate_on_submit():
        toinen = hae_joukkue_nimella(valittu_kilpailu, form.nimi.data)

        if toinen:
            form.nimi.errors.append("Joukkue on jo olemassa!")
        else:
            # koostetaan lomakkeen tiedot
            joukkue = {
                'nimi': form.nimi.data,
                'sarja': form.sarja.data,
                # poistetaan tyhjät jäsenkentät
                'jasenet': str([_field.data for _field in form.jasenet if _field.data != ""])
            }

            # lisätään uusi joukkue ilman salasanaa, funktio palauttaa lisätyn id:n
            joukkue['id'] = lisaa_joukkue(joukkue)
            # hashataan salasana saadulla id:llä
            joukkue['salasana'] = hashaa_salasana(joukkue['id'], form.salasana.data)
            # päivitetään joukkueen tiedot, jotta myös salasana tallentuu
            paivita_joukkue(joukkue)

            # lisätään viesti joukkueen tallentamisesta
            viesti = {
                'viesti': f"Joukkue {joukkue['nimi']} tallennettu!",
                'class': 'message info'
            }
    
    # haetaan joukkueet ja näytetään sivu
    joukkueet = hae_joukkueet(sarja_id=valittu_sarja)
    return render_template('admin/listaa_joukkueet.html',
                            items=joukkueet,
                            form=form,
                            viesti=viesti,
                            urlstring='admin.muokkaa_joukkuetta',
                            action_url=url_for('admin.listaa_joukkueet'))



@bp.route('/joukkueet/muokkaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def muokkaa_joukkuetta():
    """ Joukkueen muokkaukseen käytettävä sivu """

    # toinen turvonnut funktio, mutta en jaksa pilkkoa...

    # haetaan valittu joukkue, ensisijaisesti pyynnön parametreista, toissijaisesti sessiosta
    valittu_joukkue = request.args.get('id', session.get('valittu').get('joukkue'))
    valittu_sarja = session.get('valittu').get('sarja')
    valittu_kilpailu = session.get('valittu').get('kilpailu')
    
    # jos joukkuetta (tai kilpailua) ei ole valittu, ohjataan joukkuelistaukseen
    if not (valittu_joukkue or valittu_kilpailu):
        return redirect(url_for('admin.listaa_joukkueet'))

    # tallennetaan tieto valitusta joukkueesta sessioon
    session['valittu'] = {
        'kilpailu': valittu_kilpailu,
        'sarja': valittu_sarja,
        'joukkue': valittu_joukkue
    }

    # haetaan kaikki valitun kilpailun sarjat tietokannasta ja muokataan tupleiksi
    sarjat = hae_sarjat(kilpailu_id=valittu_kilpailu)
    sarja_tuplet = [(sarja['id'], sarja['nimi']) for sarja in sarjat.values()]

    # luodaan muokkauslomake ja lisätään haetut sarjat vaihtoehdoiksi
    form = MuokkausForm()
    form.sarja.choices = sarja_tuplet

    # haetaan valitun joukkueen tiedot ja leimaukset
    joukkue_dict = hae_joukkue(valittu_joukkue)
    leimaukset = hae_joukkueen_leimaukset(valittu_joukkue)

    if not joukkue_dict:
        return redirect(url_for('admin.listaa_joukkueet'))
        
    viesti = None

    # jos sivu ladataan ensimmäistä kertaa, täytetään muokkauslomake valitun joukkueen tiedoilla
    if request.method == 'GET':
        
        # muunnetaan joukkue olioksi jotta ei tarvitse mapata kenttiä käsin
        joukkue = Joukkue(**joukkue_dict)
        form.process(obj=joukkue)
    
    # jos POST-pyyntö, tarkistetaan lomake
    elif form.validate_on_submit():

        # tarkistetaan halutaanko joukkue poistaa ennen muun lomakkeen käsittelyä
        if form.poista.data:
            # poistetaan vain jos joukkueella ei ole leimauksia
            if len(leimaukset) == 0:
                poista_joukkue(valittu_joukkue)
                return redirect(url_for('admin.listaa_joukkueet'))
            else:
                viesti = {
                    'viesti': "Joukkuetta ei voida poistaa: joukkueella on leimattuja rasteja!",
                    'class': 'message error'
                }

        # jos ei poisteta
        else:
            toinen = hae_joukkue_nimella(valittu_kilpailu, form.nimi.data)

            if toinen and int(toinen['id']) != int(valittu_joukkue):
                form.nimi.errors.append("Joukkue on jo olemassa!")
            else:
                # koostetaan lomakkeen tiedot dictionaryyn
                joukkue = {
                    'id': valittu_joukkue,
                    'nimi': form.nimi.data,
                    # salasana päivitetään vain jos sitä on muokattu, muuten käytetään vanhaa salasanaa (nyt voidaan käyttää samaa querya)
                    'salasana': hashaa_salasana(int(valittu_joukkue), form.salasana.data) if form.salasana.data != "" else joukkue_dict.get('salasana'),
                    'sarja': form.sarja.data,
                    # poistetaan tyhjät jäsenkentät
                    'jasenet': str([_field.data for _field in form.jasenet if _field.data != ""])
                }

                # päivitetään joukkueen tiedot kantaan
                paivita_joukkue(joukkue)

                # näytetään viesti tallennuksen onnistumisesta
                viesti = {
                    'viesti': "Tiedot tallennettu!",
                    'class': 'message info'
                }

    # näytetään joukkueen muokkaussivu
    # (samaa pohjaa käytetään monessa yhteydessä, sivun sisältö määritetään roolin ja moodin perusteella)
    return render_template('admin/muokkaa_joukkuetta.html',
                            form=form,
                            leimaukset=leimaukset,
                            mode='edit',
                            role='admin',
                            viesti=viesti,
                            action_url=url_for('admin.muokkaa_joukkuetta'))



@bp.route('/rastit')
def listaa_rastit():
    """ Kaikki valitun kilpailun rastit näyttävä sivu """

    # haetaan valitun kilpailun tiedot sessiosta
    valittu_kilpailu = session.get('valittu').get('kilpailu')

    # jos kilpailua ei ole valittu, ohjataan takaisin kilpailulistaukseen
    if not valittu_kilpailu:
        return redirect(url_for('admin.listaa_kilpailut'))
    
    # haetaan rastit ja näytetään sivu
    rastit = hae_kilpailun_rastit_ja_leimaukset(kilpailu_id=valittu_kilpailu)
    return render_template('admin/listaa_rastit.html', rastit=rastit)



@bp.route('/leimaukset/muokkaa', methods=['GET', 'POST'])
def muokkaa_leimausta():
    """ Leimauksen muokkaukseen käytettävä sivu """
    
    # haetaan valitun kilpailun tiedot sessiosta
    valittu_kilpailu = session.get('valittu').get('kilpailu')

    # haetaan leimauksen tiedot joko pyynnön parametreista tai lomakkeelta
    joukkue_id = request.args.get('joukkue', session.get('valittu').get('joukkue'))
    vanha_aika = request.args.get('aika', request.form.get('vanha_aika'))
    vanha_rasti = request.args.get('rasti', request.form.get('vanha_rasti'))

    # jos leimauksen yksilöintitietoja ei lóydy, palataan takaisin joukkuelistaukseen
    if not (vanha_aika or vanha_rasti or joukkue_id):
        return redirect(url_for('admin.muokkaa_joukkuetta'))

    # luodaan muokkauslomake
    form = LeimausForm()

    # haetaan kilpailun rastit ja lisätään lomakkeelle vaihtoehdoiksi
    rastit = hae_kilpailun_rastit(kilpailu_id=valittu_kilpailu )
    rastituplet = [(rasti['id'], rasti['koodi']) for rasti in rastit]
    form.rasti.choices = rastituplet

    # jos sivu ladataan ensimmäistä kertaa, täytetään lomakkeen tiedot valmiiksi
    if request.method == 'GET':
        form.rasti.data = int(vanha_rasti)
        form.aika.data = datetime.fromisoformat(vanha_aika)

        # vanhat tiedot tallennetaan piilokenttiin, jotta muokattava leimaus saadaan tunnistettua
        form.vanha_rasti.data = int(vanha_rasti)
        form.vanha_aika.data = vanha_aika

    # jos POST-pyyntö ja lomake validi
    elif form.validate_on_submit():

        if form.poista.data:
            # poistetaan leimaus jos poistokenttä on valittuna
            poista_leimaus(joukkue_id, vanha_aika, vanha_rasti)
        else:
            # haetaan päivitetyt tiedot lomakkeelta ja päivitetään kanta
            uusi_aika = form.aika.data.isoformat(sep=' ')
            uusi_rasti = form.rasti.data
            print(joukkue_id, uusi_aika, uusi_rasti, vanha_aika, vanha_rasti)
            paivita_leimaus(joukkue_id, uusi_aika, uusi_rasti, vanha_aika, vanha_rasti)

        # uudelleenohjataan joukkueen muokkaussivulle
        return redirect(url_for('admin.muokkaa_joukkuetta'))
    else:
        print(form.errors)


    return render_template('admin/muokkaa_leimausta.html', form=form)
