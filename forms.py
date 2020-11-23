from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email

class RegistrationForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    dob = DateField('Your Date of Birth', validators=[DataRequired()], format='%d-%m-%Y')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
