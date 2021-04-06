from flask import Blueprint
from firebase_admin import firestore
from flask.helpers import make_response
from data import data

bp = Blueprint('init_db', __name__, url_prefix='')


@bp.route('/init_db', methods=["GET"])
def init():
    def delete_collection(coll_ref, batch_size):
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            print(f'Deleting doc {doc.id} => {doc.to_dict()}')
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return delete_collection(coll_ref, batch_size)

    try:
        db = firestore.client()
        
        print("creating client")

        kilpailut_ref = db.collection('kilpailut')

        # delete_collection(kilpailut_ref, None)

        for kilpailu in data.kilpailut:
            print("adding ", kilpailu['nimi'])
            kilpailu_ref = kilpailut_ref.document(kilpailu['nimi'])
            kilpailu_ref.set({
                'loppuaika': kilpailu['loppuaika'],
                'alkuaika': kilpailu['alkuaika']})

            sarjat_ref = kilpailu_ref.collection('sarjat')
            print("creating sarjat_ref")

            for sarja in data.sarjat:
                if sarja['kilpailu'] == kilpailu['nimi']:
                    print("adding ", sarja['nimi'])
                    sarja_ref = sarjat_ref.document(sarja['nimi'])
                    sarja_ref.set({
                        'kesto': sarja['kesto']
                    })

                    sarja_ref.collection('joukkueet')

        rastit_ref = db.collection('kilpailut/Jäärogaining/rastit')
        print("creating rastit_ref")

        for rasti in data.rastit:
            rastit_ref.add(rasti)
        print("done")

        return make_response({'status': 'OK'}, 200)
    except Exception as e:
        print("error:")
        print(e.with_traceback())
        return make_response({'status': 'ERROR', 'message': e.__cause__}, 500)
    
