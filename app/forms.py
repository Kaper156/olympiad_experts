from app.models import Olympiad, Criterion, SubCriterion, Aspect, Calculation, User, ExpertAssessment, Member
from flask.ext.wtf import Form
from wtforms import SelectField, FormField, PasswordField
from wtforms_alchemy import model_form_factory, ModelFormField
from wtforms.validators import DataRequired
from app import db

ModelForm = model_form_factory(Form)


class MemberForm(ModelForm, Form):
    class Meta:
        model = Member


class OlympiadForm(ModelForm, Form):
    class Meta:
        model = Olympiad
        date_format = '%d.%m.%Y'

    members = ModelFormField(label='Участники', form_class=MemberForm)


class CriterionForm(ModelForm, Form):
    class Meta:
        model = Criterion


class SubCriterionForm(ModelForm, Form):
    class Meta:
        model = SubCriterion


class CalculationForm(ModelForm, Form):
    class Meta:
        model = Calculation


class AspectForm(ModelForm, Form):
    class Meta:
        model = Aspect
        include = ['calculation_id']
    calculation_id = SelectField(label='Метод вычисления', coerce=int)

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        Form.__init__(self, *args, **kwargs)
        self.calculation_id.choices = [(c.id, c.name) for c in db.session.query(Calculation).all()]


class LoginForm(ModelForm, Form):
    class Meta:
        model = User
    password = PasswordField(label='Пароль')


class ExpertAssessmentForm(ModelForm, Form):
    class Meta:
        model = ExpertAssessment
        include = ['member_assessment_id']


