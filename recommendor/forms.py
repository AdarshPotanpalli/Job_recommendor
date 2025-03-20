from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from recommendor.models import User

class RegisterForm(FlaskForm):
    
    def validate_username(self, username_to_check):
        user = User.query.filter_by(user_name = username_to_check.data).first()
        if user:
            raise ValidationError('This Username already exists, try another Username!')
        
    def validate_email(self, email_to_check):
        email = User.query.filter_by(email_address = email_to_check.data).first()
        if email:
            raise ValidationError('This Email Address already exists, try another Email Address!')
    
    username = StringField(label = "Username :", validators= [Length(min=2, max = 15), DataRequired()])
    email = EmailField(label = "Email Address :", validators= [Email(), DataRequired()])
    password1 = PasswordField(label = "Password :", validators= [Length(min = 6, max = 30), DataRequired()])
    password2 = PasswordField(label = "Confirm Password :", validators= [EqualTo('password1'), DataRequired()])
    submit = SubmitField(label = "Create Account")
    
class LoginForm(FlaskForm):
    
    username = StringField(label = "Username", validators= [DataRequired()])
    password = PasswordField(label = "Password", validators= [DataRequired()])
    submit = SubmitField(label = "Login")
    
class ResumeUploadForm(FlaskForm):
    submit = SubmitField(label = 'Upload & Get Recommendations!')
    
class ArchiveForm(FlaskForm):
    submit = SubmitField(label = 'More like this')