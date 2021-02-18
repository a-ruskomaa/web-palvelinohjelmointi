import hashlib


def check_password(password: str, team_id:int, hash: str):
    m = hashlib.sha512()
    m.update( str(team_id).encode("UTF-8") )
    m.update( str(password).encode("UTF-8") )
    pw_hash = m.hexdigest()

    return pw_hash == hash