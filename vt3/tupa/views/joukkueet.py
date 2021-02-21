from sqlite3.dbapi2 import Row
from flask import Blueprint, request, render_template, session
import ast
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.fields.core import FieldList
from tupa.modules.data import hae_monta, hae_yksi, lisaa
from tupa.helpers.decorators import roles_allowed

bp = Blueprint('joukkueet', __name__, url_prefix='/joukkueet')

######### REITIT ########

@bp.route('/listaa', methods=['GET'], strict_slashes=False)
@roles_allowed(roles=['joukkue'])
def listaa():
    kilpailu_id, kilpailu_nimi = session['valittu']['kilpailu']
    _, joukkue_nimi = session['valittu']['joukkue']

    sarjat_ja_joukkueet = _hae_sarjat_ja_joukkueet(kilpailu_id=kilpailu_id)
    print(sarjat_ja_joukkueet)
    # for joukkue in _hae_joukkueet():
    #     print(joukkue['sarja_nimi'])
    #     print(joukkue['joukkue_nimi'])
    return render_template('joukkueet/lista.html', sarjat=sarjat_ja_joukkueet, kilpailu_nimi=kilpailu_nimi, joukkue_nimi=joukkue_nimi)


@bp.route('/muokkaa', methods=['GET', 'POST'], strict_slashes=False)
@roles_allowed(roles=['joukkue'])
def muokkaa():
    kilpailu_id, kilpailu_nimi = session['valittu']['kilpailu']
    joukkue_id, joukkue_nimi = session['valittu']['joukkue']
    form = _luo_muokkausform(kilpailu_id, joukkue_id)

    if form.validate_on_submit():
        print("VALID!")
        joukkue = {
            'id': int(joukkue_id),
            'nimi': form.nimi.data,
            'sarja': int(form.sarja.data),
            'jasenet': str([_field.data for _field in form.jasenet if _field.data != ""])
        }

        _tallenna_joukkue(joukkue)
    else:
        print("INVALID")
        print(form.errors)
    
    return render_template('joukkueet/muokkaa.html', form=form, kilpailu_nimi=kilpailu_nimi, joukkue_nimi=joukkue_nimi)


def _luo_muokkausform(valittu_kilpailu, valittu_joukkue):
    sarjat = _hae_sarjat(kilpailu_id=valittu_kilpailu)
    sarja_tuplet = tuple((sarja['id'], sarja['nimi']) for sarja in sarjat.values())

    joukkue = _hae_joukkue(joukkue_id=valittu_joukkue)

    def validate_jasenet(form, field):
        jasenet = [_field.data for _field in form.jasenet if _field.data != ""]
        if not 2 <= len(jasenet) <= 5:
            raise validators.ValidationError("Anna 2-5 jäsentä")

    class MuokkausForm(FlaskForm):
        nimi = StringField('nimi', validators=[validators.InputRequired(message='Syötä arvo!')], default=joukkue['nimi'])
        sarja = RadioField('sarja', choices=sarja_tuplet, default=str(joukkue['sarja']))
        jasenet = FieldList(StringField(f"jäsen", validators=[validate_jasenet]), default=joukkue['jasenet'], min_entries=5)

    return MuokkausForm()
    

######## KANTAKUTSUT ########


def _hae_sarjat_ja_joukkueet(kilpailu_id: int) -> dict:
    sql = """
    SELECT sarjat.id AS sarja_id,
           sarjat.nimi AS sarja_nimi,
           joukkueet.id AS joukkue_id,
           joukkueet.nimi AS joukkue_nimi,
           joukkueet.jasenet AS joukkue_jasenet
    FROM joukkueet
    JOIN sarjat ON joukkueet.sarja = sarjat.id
    JOIN kilpailut ON sarjat.kilpailu = kilpailut.id
    WHERE sarjat.kilpailu = :kilpailu_id
    ORDER BY
        sarja_nimi ASC,
        lower(joukkue_nimi) ASC"""

    params = {'kilpailu_id': kilpailu_id}

    rivit = hae_monta(sql, params)
    return _luo_sarja_dict(rivit)


def _hae_sarjat(kilpailu_id: int) -> dict:
    sql = """SELECT id AS sarja_id,
                    nimi AS sarja_nimi
            FROM sarjat
            WHERE sarjat.kilpailu = :kilpailu_id
            ORDER BY sarja_nimi ASC"""

    params = {'kilpailu_id': kilpailu_id}
    rivit = hae_monta(sql, params)
    return _luo_sarja_dict(rivit)


def _hae_joukkue(joukkue_id):
    sql = """SELECT id AS joukkue_id,
                    nimi AS joukkue_nimi,
                    sarja AS joukkue_sarja,
                    salasana AS joukkue_salasana,
                    jasenet AS joukkue_jasenet
            FROM joukkueet
            WHERE joukkueet.id = :joukkue_id"""

    params = {'joukkue_id': joukkue_id}
    rivi = hae_yksi(sql, params)
    return _luo_joukkue_dict(rivi)


def _tallenna_joukkue(joukkue: dict):
    sql = """UPDATE joukkueet SET
            nimi = :nimi,
            sarja = :sarja,
            jasenet = :jasenet
            WHERE id = :id"""

    params = joukkue
    lisaa(sql, params)


######## MAPPERIT ########


def _luo_sarja_dict(rivit):
    sarjat = {}
    for rivi in rivit:
        sarja_id = rivi['sarja_id']
        if not sarjat.get(sarja_id):
            sarja_nimi = rivi['sarja_nimi']
            sarjat[sarja_id] = {
                'id': sarja_id,
                'nimi': sarja_nimi,
                'joukkueet': {}}
        
        try:
            joukkue_id = rivi['joukkue_id']
            sarjat[sarja_id]['joukkueet'][joukkue_id] = _luo_joukkue_dict(rivi)
        except (KeyError, IndexError):
            continue

    return sarjat


def _luo_joukkue_dict(rivi: Row):
    joukkue_id = rivi['joukkue_id']
    joukkue_nimi = rivi['joukkue_nimi']
    joukkue_jasenet = rivi['joukkue_jasenet']
    joukkue_sarja = rivi['joukkue_sarja'] if 'joukkue_sarja' in rivi.keys() else None
    joukkue_salasana = rivi['joukkue_salasana'] if 'joukkue_salasana' in rivi.keys() else None
    
    return {
                'id': joukkue_id,
                'nimi': joukkue_nimi,
                'jasenet': ast.literal_eval(joukkue_jasenet),
                'sarja': joukkue_sarja,
                'salasana': joukkue_salasana
            }