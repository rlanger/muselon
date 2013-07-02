from flask.ext.wtf import Form, TextField, PasswordField, BooleanField, RecaptchaField
from flask.ext.wtf import Required, Email, EqualTo

class LoginForm(Form):
	name = TextField('Username', [Required()])
	password = PasswordField('Password', [Required()])
	remember = BooleanField('Remember me')


class RegistrationForm(Form):
	name = TextField('Username', [Required()])
	email = TextField('Email address', [Required(), Email()])
	password = PasswordField('Password', [Required()])
	confirm = PasswordField('Repeat Password', [
        Required(),
        EqualTo('password', message='Passwords must match')
        ])