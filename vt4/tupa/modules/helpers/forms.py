from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.fields.core import BooleanField, DateTimeField, FieldList, FloatField, SelectField
from wtforms.fields.simple import HiddenField

# sovelluksen formit koottuna samaan moduuliin


class AdminLoginForm(FlaskForm):
    salasana = PasswordField('Salasana', validators=[validators.InputRequired(message='Syötä arvo!')])


class JoukkueForm(FlaskForm):

    def validate_jasenet(form, field):
        """ Heittää poikkeuksen jos jäseniä alle 2 tai yli 5 """
        jasenet = [_field.data for _field in form.jasenet if _field.data != ""]
        if not 2 <= len(jasenet) <= 5:
            raise validators.ValidationError("Anna 2-5 jäsentä")

    nimi = StringField('Nimi', validators=[validators.InputRequired(message='Syötä arvo!')])
    jasenet = FieldList(StringField(f"Jäsen", validators=[validate_jasenet]), label="Jäsenet", min_entries=5)
    sarja = RadioField('Sarja', coerce=int)


class MuokkausForm(JoukkueForm):
    poista = BooleanField('Poista joukkue')


class LisaysForm(JoukkueForm):
    kilpailu = RadioField('Kilpailu', coerce=int)

class LeimausForm(FlaskForm):
    aika = DateTimeField('Aika', validators=[validators.InputRequired("Syötä leimauksen aika")])
    rasti = SelectField('Rasti', validators=[validators.InputRequired("Valitse leimauttu rasti")], coerce=int)
    vanha_aika = HiddenField()
    vanha_rasti = HiddenField()
    poista = BooleanField('Poista leimaus')

class RastiForm(FlaskForm):
    koodi = StringField('Koodi', validators=[validators.InputRequired(message='Syötä arvo!')])
    lat = FloatField('Lat', validators=[validators.InputRequired(message='Syötä arvo!'), validators.NumberRange(-90,90,"Anna arvo väliltä [-90, 90]")])
    lon = FloatField('Lon', validators=[validators.InputRequired(message='Syötä arvo!'), validators.NumberRange(-180,180,"Anna arvo väliltä [-180, 180]")])