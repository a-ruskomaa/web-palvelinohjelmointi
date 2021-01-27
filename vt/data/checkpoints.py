from math import sin, cos, sqrt, atan2, radians

def checkpoints_to_string(checkpoints: list):
    """Palauttaa kaikki kokonaisluvulla alkavat rastikoodit yhtenä merkkijonona"""
    def filter_checkpoints(checkpoint) -> bool:
        """Suodatetaan rasteista pois rastit joiden koodin ensimmäinen merkki ei ole numero"""
        try:
            int(checkpoint['koodi'][0])
            return True
        except ValueError:
            return False
        
    return ";".join(map(lambda cp: cp['koodi'], filter(filter_checkpoints, checkpoints)))


def find_checkpoint_by_id(id, checkpoints: list):
    try:
        id_int = int(id)
        if id_int == 0:
            return None
    except ValueError:
        return None

    for checkpoint in checkpoints:
        if checkpoint['id'] == id_int:
            return checkpoint

    return None


def get_points(koodi):
    try:
        return int(koodi[0])
    except ValueError:
        return 0


def calculate_distance(a, b):
    try:
        lat1 = radians(float(a['lat']))
        lon1 = radians(float(a['lon']))
        lat2 = radians(float(b['lat']))
        lon2 = radians(float(b['lon']))
    except ValueError:
        return 0
    # approximate radius of earth in km
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c