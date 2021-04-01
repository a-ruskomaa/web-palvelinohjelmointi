from flask import Blueprint
from flask.helpers import make_response
from firebase_admin import firestore
from tupa.helpers.auth import auth_required
import xml.etree.ElementTree as ET

bp = Blueprint('db', __name__, url_prefix='')


@bp.route('api/kilpailut/<kilpailu_id>', methods=['GET'])
@auth_required
def get_kilpailu(kilpailu_id: str):
    db = firestore.client()

    return make_response({'status': 'OK'}, 200)


@bp.route('api/kilpailut/<kilpailu_id>/sarjat', methods=['GET'])
@auth_required
def get_kilpailu_sarjat(kilpailu_id: str):
    db = firestore.client()

    sarjat_dict = {}

    sarjat_path = f"kilpailut/{kilpailu_id}/sarjat"

    sarjat = db.collection(sarjat_path).stream()

    for sarja in sarjat:
        sarjat_dict[sarja.id] = sarja.to_dict()
        sarjat_dict[sarja.id]['joukkueet'] = {}

    joukkueet = db.collection(f"joukkueet").where('kilpailu','==',kilpailu_id).order_by('nimi').stream()

    for joukkue in joukkueet:
        sarjat_dict[sarja.id]['joukkueet'].update({joukkue.id: joukkue.to_dict()})

    return make_response(sarjat_dict, 200)


@bp.route('api/kilpailut/<kilpailu_id>/rastit', methods=['GET'])
@auth_required
def get_kilpailu_rastit(kilpailu_id: str):
    db = firestore.client()

    rastit_xml = ET.Element('rastit')

    rastit = db.collection(f"kilpailut/{kilpailu_id}/rastit").stream()

    for rasti in rastit:
        data = rasti.to_dict()
        rasti_xml = ET.SubElement(rastit_xml, 'rasti')
        id_xml = ET.SubElement(rasti_xml, 'id')
        id_xml.text = rasti.id
        koodi_xml = ET.SubElement(rasti_xml, 'koodi')
        koodi_xml.text = data['koodi']
        lat_xml = ET.SubElement(rasti_xml, 'lat')
        lat_xml.text = str(data['lat'])
        lon_xml = ET.SubElement(rasti_xml, 'lon')
        lon_xml.text = str(data['lon'])

    xml_string = ET.tostring(rastit_xml,encoding='UTF-8')
    print(xml_string)

    resp = make_response(xml_string, 200)
    resp.headers['Content-type'] = 'application/xml;charset=UTF-8'
    return resp
