from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        validators.InputRequired(),
        validators.Length(min=3, max=50)
    ])
    password = PasswordField('Password', [
        validators.InputRequired(),
        validators.Length(min=8)
    ])


class LoginForm(FlaskForm):
    username = StringField('Username', [
        validators.InputRequired(),
        validators.Length(min=3, max=50)
    ])
    password = PasswordField('Password', [
        validators.InputRequired()
    ])
