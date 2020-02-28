from amalgam.models import User
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField('username',
                            validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(f'Username {username.data} is already taken. Please use a different one.')

    def validate_email(self, email):
        user_email = User.query.filter_by(email=email.data).first()
        if user_email:
            raise ValidationError(f'Email {email.data} is already taken. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UpdateAccountForm(FlaskForm):
    username = StringField('username',
                            validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg','webp'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(f'Username {username.data} is already taken. Please use a different one.')

    def validate_email(self, email):
        if current_user.email != email.data:
            user_email = User.query.filter_by(email=email.data).first()
            if user_email:
                raise ValidationError(f'Email {email.data} is already taken. Please use a different one.')
class NotebookForm(FlaskForm):
    title = StringField('Notebook Title', validators=[DataRequired()])
    description = HiddenField('Description', validators=[DataRequired()])
    submit = SubmitField('Save')

class BaseResourceForm(FlaskForm):
    title = StringField('Base Resource Title', validators=[DataRequired()])
    content = HiddenField('Content', validators=[DataRequired()])
    submit = SubmitField('Update Base Resource')

class SupportResourceForm(FlaskForm):
    title = StringField('Support Resource Title', validators=[DataRequired()])
    content = HiddenField('Content', validators=[DataRequired()])
    submit = SubmitField('Save Support Resource')
class AddPDFForm(FlaskForm):
    title = StringField('PDF Resource Title', validators=[DataRequired()])
    file = FileField('Upload PDF document', validators=[FileAllowed(['pdf']), DataRequired()])
    submit = SubmitField('Save File')
class AddJSONForm(FlaskForm):
    file = FileField('Drag or Click to upload Notebook JSON', validators=[FileAllowed(['json']), DataRequired()])


class NewBaseResourceForm(FlaskForm):
    title = StringField('Base Resource Title', validators=[DataRequired()])
    submit = SubmitField('Save Base Resource')

class NewSupportResourceForm(FlaskForm):
    title = StringField('Support Resource Title', validators=[DataRequired()])
    submit = SubmitField('Save Support Resource')