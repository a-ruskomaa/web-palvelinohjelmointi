from flask import Blueprint, render_template, session, redirect
from flask.helpers import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.fields.core import FieldList
from tupa.modules.data.dataservice import hae_joukkue, hae_sarjat, hae_sarjat_ja_joukkueet, tallenna_joukkue
from tupa.helpers.decorators import sallitut_roolit

bp = Blueprint('joukkueet', __name__, url_prefix='/joukkueet')

######### REITIT ########

@bp.route('/listaa', methods=['GET'], strict_slashes=False)
@sallitut_roolit(['joukkue'])
def listaa():
    kilpailu_id, kilpailu_nimi = session['valittu']['kilpailu']
    _, joukkue_nimi = session['valittu']['joukkue']

    sarjat_ja_joukkueet = hae_sarjat_ja_joukkueet(kilpailu_id=kilpailu_id)

    return render_template('joukkueet/lista.html', sarjat=sarjat_ja_joukkueet, kilpailu_nimi=kilpailu_nimi, joukkue_nimi=joukkue_nimi)


@bp.route('/muokkaa', methods=['GET', 'POST'], strict_slashes=False)
@sallitut_roolit(['joukkue'])
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

        tallenna_joukkue(joukkue)
        return redirect(url_for('joukkueet.listaa'))
    else:
        print("INVALID")
        print(form.errors)
    
    return render_template('joukkueet/muokkaa.html', form=form, kilpailu_nimi=kilpailu_nimi, joukkue_nimi=joukkue_nimi, mode='edit', role='joukkue')


######## FORMIT ########


def _luo_muokkausform(valittu_kilpailu, valittu_joukkue):
    sarjat = hae_sarjat(kilpailu_id=valittu_kilpailu)
    sarja_tuplet = tuple((sarja['id'], sarja['nimi']) for sarja in sarjat.values())

    joukkue = hae_joukkue(joukkue_id=valittu_joukkue)

    def validate_jasenet(form, field):
        jasenet = [_field.data for _field in form.jasenet if _field.data != ""]
        if not 2 <= len(jasenet) <= 5:
            raise validators.ValidationError("Anna 2-5 jäsentä")

    class MuokkausForm(FlaskForm):
        nimi = StringField('nimi', validators=[validators.InputRequired(message='Syötä arvo!')], default=joukkue['nimi'])
        sarja = RadioField('sarja', choices=sarja_tuplet, default=str(joukkue['sarja']))
        jasenet = FieldList(StringField(f"jäsen", validators=[validate_jasenet]), default=joukkue['jasenet'], min_entries=5)

    return MuokkausForm()
    