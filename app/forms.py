from app.models import Olympiad, Criterion, SubCriterion, Aspect, Calculation
from flask.ext.wtf import Form
from wtforms import FormField
from wtforms_alchemy import model_form_factory, ModelFieldList

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
    measurements = ModelFieldList(FormField)


class CalculationForm(ModelForm, Form):
    class Meta:
        model = Calculation

