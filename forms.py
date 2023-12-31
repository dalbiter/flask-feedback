from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField 
from wtforms.validators import InputRequired, Optional, Email


class NewUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message='Please enter a username')])
    password = PasswordField("Password", validators=[InputRequired(message='Please enter a password')])
    email = EmailField("Email", validators=[Email(message='Please enter a valid email address')])
    first_name = StringField("First Name", validators=[InputRequired(message='Please enter your first name')])
    last_name = StringField("Last Name", validators=[InputRequired(message='Please enter your last name')])

class UserLogin(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message='Please enter a username')])
    password = PasswordField("Password", validators=[InputRequired(message='Please enter a password')])

class AddFeedback(FlaskForm):
    title = StringField("Title", validators=[InputRequired(message='Please enter a title for your feedback')])
    content = TextAreaField("Feedback", validators=[InputRequired(message='Feedback must contain content')])

class EditFeedback(FlaskForm):
    title = StringField("Title")
    content = TextAreaField("Feedback")