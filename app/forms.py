from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProblemSelectionForm(FlaskForm):
    problem_selection = IntegerField("Select problem:",
                validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Select Problem')


class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField('Login')


class FileUploadForm(FlaskForm):
    allowed_extensions = []
    problem_selection = IntegerField("Specify solution:",
             validators=[DataRequired(), NumberRange(min=1)])
    file_upload = FileField("Choose a file:",
            validators=[FileRequired(), FileAllowed(allowed_extensions)])
    submit = SubmitField('Upload Solution')
