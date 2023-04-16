from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    Question = StringField('ffwf')
    Gender = RadioField('Gender', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Войти')


