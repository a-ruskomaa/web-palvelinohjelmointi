from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.fields.core import BooleanField, DateTimeField, FieldList, SelectField
from wtforms.fields.simple import HiddenField

# sovelluksen formit koottuna samaan moduuliin

class UserLoginForm(FlaskForm):
    kayttaja = StringField('Joukkue', validators=[validators.InputRequired(message='Syötä arvo!')])
    salasana = PasswordField('Salasana', validators=[validators.InputRequired(message='Syötä arvo!')])
    kilpailu = RadioField('Kilpailu', validators=[validators.InputRequired(message='Valitse yksi!')], coerce=int)


class AdminLoginForm(FlaskForm):
    kayttaja = StringField('Käyttäjä', validators=[validators.InputRequired(message='Syötä arvo!')])
    salasana = PasswordField('Salasana', validators=[validators.InputRequired(message='Syötä arvo!')])


class JoukkueForm(FlaskForm):

    def validate_jasenet(form, field):
        """ Heittää poikkeuksen jos jäseniä alle 2 tai yli 5 """
        jasenet = [_field.data for _field in form.jasenet if _field.data != ""]
        if not 2 <= len(jasenet) <= 5:
            raise validators.ValidationError("Anna 2-5 jäsentä")

    def validate_password(form, field):
        """ Heittää poikkeuksen jos salasanakentissä eri arvo """
        if form.salasana.data != form.salasana2.data:
            raise validators.ValidationError("Salasanat eivät täsmää")

    nimi = StringField('Nimi', validators=[validators.InputRequired(message='Syötä arvo!')])
    jasenet = FieldList(StringField(f"Jäsen", validators=[validate_jasenet]), label="Jäsenet", min_entries=5)


class MuokkausForm(JoukkueForm):
    sarja = RadioField('Sarja', coerce=int)
    salasana = PasswordField('Salasana', validators=[JoukkueForm.validate_password, validators.Optional()])
    salasana2 = PasswordField('Salasana uudestaan', validators=[JoukkueForm.validate_password, validators.Optional()])
    poista = BooleanField('Poista joukkue')


class LisaysForm(JoukkueForm):
    sarja = HiddenField()
    salasana = PasswordField('Salasana', validators=[JoukkueForm.validate_password, validators.InputRequired()])
    salasana2 = PasswordField('Salasana uudestaan', validators=[JoukkueForm.validate_password, validators.InputRequired()])

class LeimausForm(FlaskForm):
    aika = DateTimeField('Aika', validators=[validators.InputRequired("Syötä leimauksen aika")])
    rasti = SelectField('Rasti', validators=[validators.InputRequired("Valitse leimauttu rasti")], coerce=int)
    vanha_aika = HiddenField()
    vanha_rasti = HiddenField()
    poista = BooleanField('Poista leimaus')