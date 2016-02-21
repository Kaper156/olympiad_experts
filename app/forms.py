from app import db
from app.models import Measurement
from flask_wtf import Form
from wtforms import StringField, FloatField, TextAreaField, DateField, FieldList, SelectField
from wtforms.validators import DataRequired


class MeasurementForm(Form):
    max_balls = FloatField('Баллы', validators=[DataRequired()])
    measurement_type = SelectField('Тип измерения', validators=[DataRequired()])

    def __init__(self, **kwargs):
        Form.__init__(self, **kwargs)

        measurement_types = db.session.query(Measurement).all()
        self.measurement_type.choices = list(measurement_types)


class AspectForm(Form):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])


class OlympiadForm(Form):
    name = StringField('Название', validators=[DataRequired()])
    date = DateField('Дата начала', format='%d.%m.%Y')  # , validators=[DataRequired()]
    description = TextAreaField('Описание')
