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
    print('haetaan paikkakunnat...')
    paikkakunnat = hae_paikkakunnat()

    try:
        loydetty = next(filter(lambda pk: pk['name'] == paikkakunta, paikkakunnat))
        print('etsitään mittausasemat...')
        lahimmat = etsi_lahimmat_mittausasemat(loydetty['lat'], loydetty['lon'], 3)
        print('haetaan säätiedot...')
        havainnot = hae_saatiedot([lahin['id'] for lahin in lahimmat])
        print('haetaan sääennuste...')
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
    lat = request.args.get('lat', 0.0, type=float)
    lon = request.args.get('lon', 0.0, type=float)
    
    print('etsitään mittausasemat...')
    lahimmat = etsi_lahimmat_mittausasemat(lat, lon, 1)
    print('haetaan säätiedot...')
    havainnot = hae_saatiedot([lahin['id'] for lahin in lahimmat])
    print('etsitään lähin paikkakunta...')
    paikkakunta = etsi_lahin_paikkakunta(lat, lon)
    print('etsitään paikannimi...')
    paikannimi = hae_paikannimi(lat, lon)
    print('haetaan sääennuste...')
    ennuste = hae_saaennuste(paikkakunta[0]['url'])

    return json.dumps({
        'havainnot': havainnot,
        'ennuste': ennuste,
        'ennuste_pk': paikkakunta[0]['name'],
        'havainnot_pk': paikannimi}, default=_decimal_default), 200


@bp.route('/mittaukset', methods=['GET'])
def mittaukset():
    lat = request.args.get('lat', 0.0, type=float)
    lon = request.args.get('lon', 0.0, type=float)
    n = request.args.get('n', 1, type=int)

    lahimmat = etsi_lahimmat_mittausasemat(lat, lon, n)
    mittausdata = hae_saatiedot([lahin['id'] for lahin in lahimmat])

    return json.dumps(mittausdata, default=_decimal_default), 200


@bp.route('/ennuste', methods=['GET'])
def ennuste():
    lat = request.args.get('lat', 0.0, type=float)
    lon = request.args.get('lon', 0.0, type=float)

    paikkakunta = etsi_lahin_paikkakunta(lat, lon)

    ennuste = hae_saaennuste(paikkakunta[0]['url'])

    return json.dumps(ennuste), 200


def _decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


