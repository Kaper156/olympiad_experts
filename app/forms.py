from flask_wtf import Form
from wtforms import StringField, FloatField, TextAreaField, DateField, FieldList, SelectField
from wtforms.validators import DataRequired, NumberRange

class Editor(Form):
    name = StringField('Назание', validators=[DataRequired()])
    max_balls = FloatField('Максимум баллов', validators=[DataRequired(), NumberRange()])

class EditorOlympiad(Editor):
    description = TextAreaField('Описание')
    date = DateField('Дата проведения', validators=[DataRequired()], format='%d.%m.%Y')


