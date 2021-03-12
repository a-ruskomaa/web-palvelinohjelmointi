from collections import namedtuple
from flask import Blueprint, render_template, session, redirect
from flask.globals import request
from flask.helpers import url_for
from tupa.modules.services.data import ds
from tupa.modules.helpers.decorators import sallitut_roolit
from tupa.modules.helpers.forms import RastiForm

Rasti = namedtuple('Rasti', ['id', 'kilpailu', 'koodi', 'lat', 'lon'])

bp = Blueprint('rastit', __name__, url_prefix='/rastit')

@bp.route('/lisaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def lisaa():
    form = RastiForm()

    valittu_kilpailu = session.get('kilpailu')
    kayttaja = session.get('kayttaja')

    if form.validate_on_submit():
        rasti_dict = {
            'koodi': form.koodi.data,
            'lat': form.lat.data,
            'lon': form.lon.data
        }

        # toinen = ds.hae_rasti(kilpailu_id=valittu_kilpailu, filters={'koodi': rasti_dict['koodi']})

        # if toinen:
        #     form.koodi.errors.append("Koodi on jo olemassa!")

        # else:
        ds.lisaa_rasti(rasti=rasti_dict, kilpailu_id=valittu_kilpailu)
        return redirect(url_for('joukkueet.listaa'))

    
    return render_template('rastit/form.html',
                            form=form,
                            mode='lisaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('rastit.lisaa'))


@bp.route('/muokkaa', methods=['GET', 'POST'])
@sallitut_roolit(['admin'])
def muokkaa():
    kayttaja = session.get('kayttaja')
    valittu_kilpailu = session.get('kilpailu')

    rasti_id = request.args.get('id', request.form.get('id', type=int), type=int)
    print("rasti_id", rasti_id)
    kilpailu_id = request.args.get('kilpailu', request.form.get('kilpailu', type=int), type=int)
    print("kilpailu_id", kilpailu_id)

    rasti = ds.hae_rasti(rasti_id=rasti_id, kilpailu_id=kilpailu_id)
    kilpailu = ds.hae_kilpailu(kilpailu_id)
    
    if not (rasti and kilpailu):
        return render_template('error.html', message="Virheellinen tunniste")

    if kilpailu_id != int(valittu_kilpailu):
        return redirect(url_for('joukkueet.listaa'))

    if request.method == 'GET':
        rasti_obj = Rasti(rasti_id, kilpailu_id, rasti['koodi'], rasti['lat'], rasti['lon'])
        print("rasti_obj", rasti_obj)
        form = RastiForm(obj=rasti_obj)
    else:
        form = RastiForm()

    if form.validate_on_submit():

        if form.poista.data:
            ds.poista_rasti(rasti_id=rasti_id, kilpailu_id=kilpailu_id)
            return redirect(url_for('joukkueet.listaa'))
        
        rasti_dict = {
            'koodi': form.koodi.data,
            'lat': form.lat.data,
            'lon': form.lon.data
        }

        ds.paivita_rasti(rasti_id=rasti_id, rasti=rasti_dict, kilpailu_id=valittu_kilpailu)
        return redirect(url_for('joukkueet.listaa'))

    
    return render_template('rastit/form.html',
                            form=form,
                            mode='muokkaa',
                            roles=kayttaja['roolit'],
                            action_url=url_for('rastit.muokkaa'))