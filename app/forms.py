from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProblemSelectionForm(FlaskForm):
    problem_selection = IntegerField("Select problem:",
                validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Select Problem')
