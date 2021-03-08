from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.fields.core import BooleanField, DateTimeField, FieldList, FloatField, SelectField
from wtforms.fields.simple import HiddenField

# sovelluksen formit koottuna samaan moduuliin


class AdminLoginForm(FlaskForm):
    kilpailu = RadioField('Kilpailu', validators=[validators.InputRequired(message='Valitse yksi!')], coerce=int)
    salasana = PasswordField('Salasana', validators=[validators.InputRequired(message='Syötä arvo!')])


class JoukkueForm(FlaskForm):

    def validate_jasenet(form, field):
        """ Heittää poikkeuksen jos jäseniä alle 2 tai yli 5 """
        jasenet = [_field.data.strip() for _field in form.jasenet if _field.data.strip() != ""]
        n = len(jasenet)
        if not 2 <= n <= 5:
            raise validators.ValidationError("Anna 2-5 jäsentä")
        
        for i in range(n):
            for j in range(i + 1, n):
                if jasenet[i] == jasenet[j]:
                    raise validators.ValidationError("Jäsenet eivät voi olla saman nimisiä")

    nimi = StringField('Nimi', validators=[validators.InputRequired(message='Syötä arvo!')])
    jasenet = FieldList(StringField(f"Jäsen", validators=[validate_jasenet]), label="Jäsenet", min_entries=5)
    sarja = RadioField('Sarja', validators=[validators.InputRequired(message='Valitse sarja!')], coerce=int)


class MuokkausForm(JoukkueForm):
    id = HiddenField('Id')
    kilpailu = HiddenField('Kilpailu')
    vanha_sarja = HiddenField('Vanha sarja')
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