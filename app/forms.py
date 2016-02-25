from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement
from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory

ModelForm = model_form_factory(Form)


class OlympiadForm(ModelForm, Form):
    class Meta:
        model = Olympiad



class CriterionForm(ModelForm, Form):
    class Meta:
        model = Criterion
