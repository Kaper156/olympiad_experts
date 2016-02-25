from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement
from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory

ModelForm = model_form_factory(Form)


class OlympiadForm(ModelForm, Form):
    class Meta:
        model = Olympiad
        date_format = '%d.%m.%Y'


class CriterionForm(ModelForm, Form):
    class Meta:
        model = Criterion


class SubCriterionForm(ModelForm, Form):
    class Meta:
        model = SubCriterion


class AspectForm(ModelForm, Form):
    class Meta:
        model = Aspect


class MeasurementForm(ModelForm, Form):
    class Meta:
        model = Measurement
