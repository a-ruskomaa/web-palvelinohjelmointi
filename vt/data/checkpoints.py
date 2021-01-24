
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

# def find_start_and_end_id( checkpoints: list):
#     start_id = -1
#     end_id = -1

#     for checkpoint in checkpoints:
#         if checkpoint['koodi'] == 'LAHTO':
#             start_id = checkpoint['koodi']
#         elif checkpoint['koodi'] == 'MAALI':
#             end_id = checkpoint['koodi']

#     return (start_id, end_id)

def get_points(koodi):
    try:
        return int(koodi[0])
    except ValueError:
        return 0