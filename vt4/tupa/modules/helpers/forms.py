from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.fields.core import BooleanField, DateTimeField, FieldList, FloatField, SelectField
from wtforms.fields.simple import HiddenField
from tupa.modules.services.data import ds

# sovelluksen formit koottuna samaan moduuliin


class AdminLoginForm(FlaskForm):
    kilpailu = RadioField('Kilpailu', validators=[validators.InputRequired(message='Valitse yksi!')], coerce=int)
    salasana = PasswordField('Salasana', validators=[validators.InputRequired(message='Syötä arvo!')])


class JoukkueForm(FlaskForm):

    def validate_nimi(form, field):
        print("Validoidaan nimi")
        joukkue_id = form.id.data if hasattr(form, 'id') else -1
        kilpailu_id = int(form.kilpailu.data)
        saman_nimiset = ds.hae_joukkueet(kilpailu_id=kilpailu_id, filters={'nimi': field.data})
        print(saman_nimiset)

        if form.nimi.data in [joukkue['nimi'] for joukkue in saman_nimiset if int(joukkue.key.id) != int(joukkue_id)]:
            raise validators.ValidationError("Joukkue on jo olemassa!")


    def validate_jasenet(form, field):
        """ Heittää poikkeuksen jos jäseniä alle 2 tai yli 5 """
        print("Validoidaan jasenet")
        jasenet = [_field.data.strip() for _field in form.jasenet if _field.data.strip() != ""]
        n = len(jasenet)
        if not 2 <= n <= 5:
            raise validators.ValidationError("Anna 2-5 jäsentä")
        
        for i in range(n):
            for j in range(i + 1, n):
                if jasenet[i] == jasenet[j]:
                    raise validators.ValidationError("Jäsenet eivät voi olla saman nimisiä")

    nimi = StringField('Nimi', validators=[validators.InputRequired(message='Syötä arvo!')])
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
    id = HiddenField('Id')
    kilpailu = HiddenField('Kilpailu')
    joukkue = HiddenField('Joukkue')
    aika = DateTimeField('Aika', validators=[validators.InputRequired("Syötä leimauksen aika")])
    rasti = SelectField('Rasti', validators=[validators.InputRequired("Valitse leimauttu rasti")], coerce=int)
    poista = BooleanField('Poista leimaus')


class RastiForm(FlaskForm):

    def validate_koodi(form, field):
        sama_koodi = ds.hae_rastit(kilpailu_id=int(form.kilpailu.data), filters={'koodi': field.data})

        for koodi in sama_koodi:
            if int(koodi.key.id) != int(form.id.data):
                form.koodi.errors.append("Koodi on jo olemassa!")

    id = HiddenField('Id')
    kilpailu = HiddenField('Kilpailu')
    koodi = StringField('Koodi', validators=[validators.InputRequired(message='Syötä arvo!')])
    lat = FloatField('Lat', validators=[validators.InputRequired(message='Syötä arvo!'), validators.NumberRange(-90,90,"Anna arvo väliltä [-90, 90]")])
    lon = FloatField('Lon', validators=[validators.InputRequired(message='Syötä arvo!'), validators.NumberRange(-180,180,"Anna arvo väliltä [-180, 180]")])
    poista = BooleanField('Poista rasti')