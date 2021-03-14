from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.fields.core import BooleanField, DateTimeField, FieldList, FloatField, FormField, SelectField
from wtforms.fields.simple import HiddenField
from tupa.modules.services.data import ds

# sovelluksen formit koottuna samaan moduuliin

def strip_whitespace(s):
    if s:
        return s.strip()

class AdminLoginForm(FlaskForm):
    kilpailu = RadioField('Kilpailu', validators=[validators.InputRequired(message='Valitse yksi!')], coerce=int)
    salasana = PasswordField('Salasana', validators=[validators.InputRequired(message='Syötä arvo!')])


class JoukkueForm(FlaskForm):

    def validate_nimi(form, field):
        """ Tarkistaa, ettei nimi ole tyhjä tai jo käytössä """
        if field.data == "":
            raise validators.ValidationError("Nimi ei voi olla tyhjä!")

        joukkue_id = form.id.data if hasattr(form, 'id') else -1
        kilpailu_id = int(form.kilpailu.data)
        saman_nimiset = ds.hae_joukkueet(kilpailu_id=kilpailu_id, filters={'nimi': field.data})
        print(saman_nimiset)

        if field.data in [joukkue['nimi'] for joukkue in saman_nimiset if int(joukkue.key.id) != int(joukkue_id)]:
            raise validators.ValidationError("Joukkue on jo olemassa!")


    def validate_jasenet(form, fields):
        """ Tarkistaa, että jäseniä on 2-5 """
        jasenet = [field.data.strip() for field in fields if field.data.strip() != ""]

        n = len(jasenet)
        if not 2 <= n <= 5:
            raise validators.ValidationError("Anna 2-5 jäsentä")
        
        for i in range(n):
            for j in range(i + 1, n):
                if jasenet[i] == jasenet[j]:
                    raise validators.ValidationError("Jäsenet eivät voi olla saman nimisiä")

    nimi = StringField('Nimi', validators=[validators.InputRequired(message='Syötä arvo!')], filters=[strip_whitespace])
    jasenet = FieldList(StringField(f"Jäsen"), label="Jäsenet", min_entries=5)
    sarja = RadioField('Sarja', validators=[validators.InputRequired(message='Valitse sarja!')], coerce=int)


class MuokkausForm(JoukkueForm):
    id = HiddenField('Id')
    kilpailu = HiddenField('Kilpailu')
    vanha_sarja = HiddenField('Vanha sarja')
    poista = BooleanField('Poista joukkue')


class LisaysForm(JoukkueForm):
    kilpailu = RadioField('Kilpailu', coerce=int)


class LeimausForm(FlaskForm):

    def validate_rasti(form, field):
        """ Tarkistaa että rastia ei ole vielä leimattu """
        if form.poista.data:
            # ei validoida kenttää jos ollaan poistamassa
            field.errors = []
            raise validators.StopValidation()

        joukkue = ds.hae_joukkue(joukkue_id=int(form.joukkue.data), sarja_id=int(form.sarja.data), kilpailu_id=int(form.kilpailu.data))

        if field.data in joukkue['leimaukset'].keys() and form.id.data != field.data:
            raise validators.ValidationError("Rasti on jo leimattu!")

    id = HiddenField('Id')
    kilpailu = HiddenField('Kilpailu')
    sarja = HiddenField('Sarja')
    joukkue = HiddenField('Joukkue')
    aika = DateTimeField('Aika', validators=[validators.InputRequired("Syötä leimauksen aika")])
    rasti = SelectField('Rasti', coerce=str)
    poista = BooleanField('Poista leimaus')



class RastiForm(FlaskForm):

    def validate_koodi(form, field):
        """ Tarkistaa että rastin koodi ei ole tyhjä tai jo käytössä """
        if field.data == "":
            raise validators.ValidationError("Koodi ei voi olla tyhjä!")
        
        # haetaan kaikki kilpailun rastit rajaten koodin perusteella
        sama_koodi = ds.hae_rastit(kilpailu_id=int(form.kilpailu.data), filters={'koodi': field.data})

        id = int(form.id.data) if form.id.data != "" else -1

        # jos hakutuloksissa on rasti, jolla on sama koodi mutta eri id,
        # heitetään poikkeus
        for koodi in sama_koodi:
            if int(koodi.key.id) != id:
                raise validators.ValidationError("Koodi on jo olemassa!")

    id = HiddenField('Id')
    kilpailu = HiddenField('Kilpailu')
    koodi = StringField('Koodi', validators=[validators.InputRequired(message='Syötä arvo!')], filters=[strip_whitespace])
    lat = FloatField('Lat', validators=[validators.InputRequired(message='Syötä arvo!'), validators.NumberRange(-90,90,"Anna arvo väliltä [-90, 90]")])
    lon = FloatField('Lon', validators=[validators.InputRequired(message='Syötä arvo!'), validators.NumberRange(-180,180,"Anna arvo väliltä [-180, 180]")])
    poista = BooleanField('Poista rasti')