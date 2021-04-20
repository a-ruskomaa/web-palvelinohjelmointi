import json
from flask import Blueprint, request
from saatiedot.services.dataservice import (hae_paikkakunnat,
                                            etsi_lahin_paikkakunta,
                                            etsi_lahimmat_mittausasemat,
                                            hae_paikannimi,
                                            hae_saatiedot,
                                            hae_saaennuste)
import decimal

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/', methods=["GET"])
def index():
    return "hello", 200


@bp.route('/paikkakunnat', methods=['GET'])
def paikkakunnat():
    paikkakunnat = hae_paikkakunnat()

    return json.dumps(paikkakunnat, default=_decimal_default), 200


@bp.route('/paikkakunnat/<paikkakunta>', methods=['GET'])
def paikkakunta(paikkakunta):
    """ Reitti, jonka kautta asiakassovellus voi hakea kaikki paikkakuntakohtaiset mittaus- ja ennustetiedot.
        
        Funktio etsii url-parametrina annettua nimeä vastaavan paikkakunnan koordinaatit, etsii 3 tätä pistettä
        lähintä mittausasemaa ja hakee niiden mittaustiedot. Lisäksi funktio hakee tietokantaan tallennetusta
        url-osoitteesta paikkakunnan sääennusteen. 
        
        Nämä kannattaisi todellisuudessa jakaa omiksi reiteikseen, jotta epäonnistunut pyyntö tai pitkä vastausviive
        eivät hidastaisi datan näyttämistä asiakassovelluksessa. Palvelinsovellus kyllä toipuu yhteysvirheistä ulkoisiin
        palveluihin, mutta vastauksen muodostamisessa saattaa tällöin kestää turhan pitkään. """
    paikkakunnat = hae_paikkakunnat()

    try:
        loydetty = next(filter(lambda pk: pk['name'] == paikkakunta, paikkakunnat))
        lahimmat = etsi_lahimmat_mittausasemat(loydetty['lat'], loydetty['lon'], 3)
        havainnot = hae_saatiedot([lahin['id'] for lahin in lahimmat])
        ennuste = hae_saaennuste(loydetty['url'])

        return json.dumps({
            'havainnot': havainnot,
            'ennuste': ennuste,
            'ennuste_pk': paikkakunta,
            'havainnot_pk': paikkakunta}, default=_decimal_default), 200
    except StopIteration as e:
        return {'status': 'Not found'}, 400


@bp.route('/koordinaatit', methods=['GET'])
def koordinaatit():
    """ Reitti, jonka kautta asiakassovellus voi hakea kaikki annettuja koordinaatteja vastaavat mittaus- ja ennustetiedot.
    
    Funktio etsii pyynnön parametreina annettuja koordinaatteja lähimmän mittausaseman ja hakee sen mittaustiedot. Lisäksi
    funktio etsii pisteitä lähinnä olevan paikkakunnan, hakee tietokantaan tallennetusta url-osoitteesta sen sääennusteen.
    Jos koordinaatit sijaitsevat Suomessa, hakee funktio myös MML:n API:sta pisteitä vastaavan paikan nimen. 
    
    Nämä kannattaisi todellisuudessa jakaa omiksi reiteikseen, jotta epäonnistunut pyyntö tai pitkä vastausviive
    eivät hidastaisi datan näyttämistä asiakassovelluksessa. Palvelinsovellus kyllä toipuu yhteysvirheistä ulkoisiin
    palveluihin, mutta vastauksen muodostamisessa saattaa tällöin kestää turhan pitkään. """
    lat = request.args.get('lat', 0.0, type=float)
    lon = request.args.get('lon', 0.0, type=float)
    
    lahimmat = etsi_lahimmat_mittausasemat(lat, lon, 1)
    havainnot = hae_saatiedot([lahin['id'] for lahin in lahimmat])
    paikkakunta = etsi_lahin_paikkakunta(lat, lon)
    paikannimi = hae_paikannimi(lat, lon)
    ennuste = hae_saaennuste(paikkakunta[0]['url'])

    return json.dumps({
        'havainnot': havainnot,
        'ennuste': ennuste,
        'ennuste_pk': paikkakunta[0]['name'],
        'havainnot_pk': paikannimi}, default=_decimal_default), 200


# @bp.route('/mittaukset', methods=['GET'])
# def mittaukset():
#     lat = request.args.get('lat', 0.0, type=float)
#     lon = request.args.get('lon', 0.0, type=float)
#     n = request.args.get('n', 1, type=int)

#     lahimmat = etsi_lahimmat_mittausasemat(lat, lon, n)
#     mittausdata = hae_saatiedot([lahin['id'] for lahin in lahimmat])

#     return json.dumps(mittausdata, default=_decimal_default), 200


# @bp.route('/ennuste', methods=['GET'])
# def ennuste():
#     lat = request.args.get('lat', 0.0, type=float)
#     lon = request.args.get('lon', 0.0, type=float)

#     paikkakunta = etsi_lahin_paikkakunta(lat, lon)

#     ennuste = hae_saaennuste(paikkakunta[0]['url'])

#     return json.dumps(ennuste), 200


def _decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


