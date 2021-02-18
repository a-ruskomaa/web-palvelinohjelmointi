from tupa.modules.domain.checkpoints import find_checkpoint_by_id, get_points, calculate_distance
from datetime import datetime, timedelta

def calculate_statistics(team: dict, checkpoints: list):
    """Laskee joukkueen pisteet, kokonaisajan ja kulkeman matkan"""
    punches = team['rastit']

    # seulotaan rastileimauksista vain kelvolliset leimaukset
    valid_punches, start_punch, end_punch = _parse_punches(punches, checkpoints)

    # Lasketaan kelvollisten leimausten perusteella joukkueen pisteet, aika ja kulkema matka
    points = _calculate_points(valid_punches)
    time = _calculate_time(start_punch, end_punch)
    distance = _calculate_total_distance(start_punch, end_punch, valid_punches)

    return points, time, distance



def _calculate_time(start_punch, end_punch) -> timedelta:
    """Laskee lähtö- ja maalileimauksen välisen ajan"""
    if start_punch and end_punch:
        return datetime.fromisoformat(end_punch['aika']) - datetime.fromisoformat(start_punch['aika'])
    
    return timedelta(0)


def _calculate_total_distance(start_punch, end_punch, valid_punches: list):
    """Laskee joukkueen kulkeman kokonaismatkan laillisten rastileimauksien perusteella"""
    if not (start_punch and end_punch):
        return 0

    # Luodaan iteraattori aikajärjestyksessä olevista leimauksista
    punch_iter = iter(sorted([start_punch, end_punch, *valid_punches], key=lambda x: x['aika']))

    # Iteroidaan leimausten läpi ja lasketaan kokonaismatka
    total = 0
    checkpoint_a = next(punch_iter)
    for checkpoint_b in punch_iter:
        total += calculate_distance(checkpoint_a['rasti'], checkpoint_b['rasti'])
        checkpoint_a = checkpoint_b

    return total



def _calculate_points(valid_punches: list):
    """Laskee pisteet annetuista rastileimauksista"""
    total = 0
    for punch in valid_punches:
        total += get_points(punch['rasti'])

    return total



def _parse_punches(punches: list, checkpoints: list):
    """Seuloo rastileimauksista vain kelvolliset leimaukset. Leimatun rastin id:n
    on vastattava todellista rastia ja leimauksen ajankohdan tulee olla lähtö- ja maalileimauksen
    välissä.
    
    Palauttaa listan leimauksia muodossa: [{aika, rasti={id, lat, lon, koodi}}]
    """

    punched_checkpoints = set()
    parsed_punches = []
    valid_punches = []
 
    # Muunnetaan rastileimaukset muotoon {aika, {id, lat, lon, koodi}} ja karsitaan pois epäkelvot leimaukset
    for punch in punches:
        checkpoint = find_checkpoint_by_id(punch['rasti'], checkpoints)
        if checkpoint:
            parsed_punches.append({'aika': punch['aika'], 'rasti':checkpoint.copy()})

    start_punch, end_punch = _get_start_end_punches(parsed_punches)

    # Karsitaan toisella iteraatiolla leimaukset, jotka ovat sallitun aikavälin ulkopuolella
    # tai leimattu useammin kuin kerran
    for punch in parsed_punches:
        if _is_valid_punch(punch, start_punch, end_punch, punched_checkpoints):
            valid_punches.append(punch)

    return valid_punches, start_punch, end_punch


def _get_start_end_punches(parsed_punches: list):
    """Etsii myöhäisimmän lähtöleimauksen ja ensimmäisen maalileimauksen.
    
    Palauttaa leimaukset tuplena (lähtö, maali)"""
    start_datetime = None
    start_punch = None
    end_datetime = None
    end_punch = None

    # Etsitään ensimmäisellä iteraatiolla myöhäisin lähtöleimaus
    for punch in parsed_punches:
        if punch['rasti']['koodi'] == 'LAHTO':
            start_timestamp = punch['aika']
            temp_datetime = datetime.fromisoformat(start_timestamp) if start_timestamp else None

            # Hyväksytään ensimmäinen vastaantuleva lähtöleimaus sekä leimaus jonka
            # ajankohta on myöhemmin kuin aiemmin löydetty lähtöleimaus
            if (not start_datetime or temp_datetime > start_datetime):
                start_datetime = temp_datetime
                start_punch = punch

    # Etsitään toisella iteraatiolla ensimmäinen maalileimaus (vain jos lähtöleimaus löytyi)
    if start_datetime:
        for punch in parsed_punches:
            if punch['rasti']['koodi'] == 'MAALI':
                end_timestamp = punch['aika']
                temp_datetime = datetime.fromisoformat(end_timestamp) if end_timestamp else None

                # Hyväksytään ensimmäinen vastaantuleva maalileimaus sekä leimaus jonka
                # leimauksen ajankohta on myöhemmin kuin aiemmin löydetty lähtöleimaus.
                # Leimauksen tulee olla lähtöleimauksen jälkeen.
                if (temp_datetime > start_datetime and (not end_datetime or temp_datetime < end_datetime)):
                    end_datetime = temp_datetime
                    end_punch = punch

    return (start_punch, end_punch)


def _is_valid_punch(punch, start_punch, end_punch, punched_checkpoints: set):
    """Tarkistaa onko rastileimauksen aikaleima lähtö- ja maalileimauksen välissä ja
    onko rasti leimattu vain yhden kerran"""

    # Jos rasti on jo leimattu, ei kelpuuteta toista leimausta
    if punch['rasti']['koodi'] in punched_checkpoints:
        return False

    # Muunnetaan aikaleimat datetime-objekteiksi vertailua varten
    timestamp = datetime.fromisoformat(punch['aika'])
    start_timestamp = datetime.fromisoformat(start_punch['aika'])
    end_timestamp = datetime.fromisoformat(end_punch['aika'])

    # Kelpuutetaan leimaus vain jos se on sallitulla aikavälillä
    valid = start_timestamp < timestamp < end_timestamp
    if valid:
        # Lisätään kelvollisten leimausten joukkoon
        punched_checkpoints.add(punch['rasti']['koodi'])

    return valid
