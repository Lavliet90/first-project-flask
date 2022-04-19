from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[Email()])
    psw = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=100)])
    remember = BooleanField('Remember', default=False)
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    name = StringField('Name: ', validators=[Length(min=4, max=100)])
    email = StringField('Email: ', validators=[Email()])
    psw = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=100)])
    psw2 = PasswordField('Repit password: ', validators=[DataRequired(), EqualTo('psw')])
    submit = SubmitField('Registration')
