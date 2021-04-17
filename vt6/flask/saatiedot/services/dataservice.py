from flask.globals import current_app
import xml.etree.ElementTree as ET
from saatiedot import db, cache
from sqlalchemy import sql
import json
import gzip
import urllib
from math import sin, cos, sqrt, atan2, radians

DIGITRAFFIC_METADATA_URL='https://tie.digitraffic.fi/api/v3/metadata/weather-stations'
DIGITRAFFIC_API_URL='https://tie.digitraffic.fi/api/v1/data/weather-data/'
MML_API_URL='https://avoin-paikkatieto.maanmittauslaitos.fi/geocoding/v1/pelias/reverse'

@cache.cached(timeout=86400, key_prefix='paikkakunnat')
def hae_paikkakunnat():
    results = db.session.execute("SELECT name, lat, lon, url FROM weather WHERE countrycode = 'FI'")
    res_arr = [dict(result) for result in results]
    return res_arr

@cache.memoize(timeout=86400)
def etsi_lahin_paikkakunta(lat, lon):
    query = sql.text(
        "SELECT name, lat, lon, (point(:lon,:lat) <@> point(lon,lat)) As dist, url "
        "FROM weather "
        "ORDER BY dist ASC "
        "LIMIT 1"
    )
    results = db.session.execute(query, params={'lon':lon, 'lat':lat})
    res_arr = [dict(result) for result in results]

    return res_arr

@cache.cached(timeout=86400, key_prefix='mittausasemat')
def hae_mittausasemat():
    user_agent = "TIES4080 demo application roarusko@jyu.fi"
    req = urllib.request.Request(url=DIGITRAFFIC_METADATA_URL, headers={'Accept-Encoding': 'gzip', 'User-Agent': user_agent})
    with urllib.request.urlopen(req) as response:
        gzip_res = gzip.GzipFile(fileobj=response)
        data = json.load(gzip_res)

        asemat = [{
            'id': station['id'],
            'coordinates': {
                'lon':station['geometry']['coordinates'][0],
                'lat':station['geometry']['coordinates'][1]
                }} for station in data['features']]

        return asemat

@cache.memoize(timeout=3600)
def hae_mittausdata(id):
    req = urllib.request.Request(url=DIGITRAFFIC_API_URL+str(id), headers={'Accept-Encoding': 'gzip'})

    saatiedot = {
        'ILMA': None,
        'MAA_1': None,
        'TIE_1': None,
        'TUULENSUUNTA': None,
        'KESKITUULI': None,
        'ILMAN_KOSTEUS': None,
        'NAKYVYYS': None,
    }

    try:
        with urllib.request.urlopen(req) as response:
            print(f"Haettu mittausdata, id: {id}")
            print(response)
            gzip_res = gzip.GzipFile(fileobj=response)
            data = json.load(gzip_res)


            # TODO try catch
            for mittari in data['weatherStations'][0]['sensorValues']:
                if mittari['name'] in saatiedot.keys():
                    saatiedot[mittari['name']] = mittari['sensorValue']
    except Exception as e:
        print(f"Virhe mittausdatan hakemisessa! id: {id}")
        print(e)

    return saatiedot

def etsi_lahimmat_mittausasemat(lat, lon, n):
    mittausasemat = hae_mittausasemat()

    lahimmat = [None for i in range(n)]
    lahimmat_dist = [None for i in range(n)]

    point = {
        'lat': lat,
        'lon': lon
    }

    for asema in mittausasemat:
        dist = _calculate_distance(point, asema['coordinates'])

        for i, prev_dist in enumerate(lahimmat_dist):
            if dist < 100 and (not prev_dist or dist <= prev_dist):
                # jätetään samassa sijainnissa sijaitsevat mittausasemat huomioimatta
                if (dist == prev_dist):
                    break
                # lisätään mittausasema oikeaan kohtaan taulukkoa
                lahimmat.insert(i,asema['id'])
                lahimmat_dist.insert(i,dist)
                # katkaistaan taulukosta yli jäänyt osuus
                lahimmat = lahimmat[:n]
                lahimmat_dist = lahimmat_dist[:n]
                break
        
    return [{'id': lahimmat[i], 'dist': lahimmat_dist[i]} for i, _ in enumerate(lahimmat)]


def hae_saatiedot(ids):
    data = [hae_mittausdata(id) for id in ids]

    saatiedot = {
        'ILMA': None,
        'MAA_1': None,
        'TIE_1': None,
        'TUULENSUUNTA': None,
        'KESKITUULI': None,
        'ILMAN_KOSTEUS': None,
        'NAKYVYYS': None,
    }

    saatiedot_datapoints = {
        'ILMA': 0,
        'MAA_1': 0,
        'TIE_1': 0,
        'TUULENSUUNTA': 0,
        'KESKITUULI': 0,
        'ILMAN_KOSTEUS': 0,
        'NAKYVYYS': 0,
    }

    # summataan mittaustulokset yhteen
    for d in data:
        for k, v in d.items():
            print("k", k)
            print("v", v)
            if not v:
                continue
            if not saatiedot[k]:
                saatiedot[k] = v
            else:
                saatiedot[k] += v
            saatiedot_datapoints[k] += 1

    # Lasketaan keskiarvo jakamalla kenttäkohtaisesti mittaustulosten määrällä.
    # Tuulen suunta pitäisi oikeasti keskiarvottaa muulla tavoin, koska
    # esim. 358 + 2 = 180 (eikä 0), mutta nyt teen tietoisen virheen.
    for k,v in saatiedot.items():
        if saatiedot[k]:
            saatiedot[k] /= saatiedot_datapoints[k]

    return saatiedot

@cache.memoize(timeout=3600)
def hae_paikannimi(lat, lon):
    api_key = current_app.config.get('MML_API_KEY')
    params = urllib.parse.urlencode({'point.lat': lat, 'point.lon': lon, 'api-key': api_key})
    req = urllib.request.Request(url=f"{MML_API_URL}?{params}", method="GET")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)

            return data['features'][0]['properties']['label:municipality']
    except Exception as e:
        print("Virhe paikannimen etsimisessä:")
        print(e)

        return "Tuntematon"

@cache.memoize(timeout=3600)
def hae_saaennuste(url):
    req = urllib.request.Request(url=urllib.parse.quote(url, safe='/:'), headers={'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req) as response:
        gzip_res = gzip.GzipFile(fileobj=response)
        xml = ET.parse(gzip_res)
        # root = xml.getroot()
        forecast = xml.find('forecast')
        tabular = forecast.find('tabular')
        times = tabular.iterfind('time')

        lampotilat = [
            {'aika': time.get('from').replace("T", " "),
            'lampotila': time.find('temperature').get('value')} for time in times]

        return lampotilat[:10]


def _calculate_distance(point_a, point_b):
    """Laskee kahden rastin välisen etäisyyden"""
    try:
        # Muunnetaan koordinaatit asteista radiaaneiksi
        lat1 = radians(float(point_a['lat']))
        lon1 = radians(float(point_a['lon']))
        lat2 = radians(float(point_b['lat']))
        lon2 = radians(float(point_b['lon']))
    except ValueError:
        return 0
    # maan ympärysmitta kilometreissä
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c