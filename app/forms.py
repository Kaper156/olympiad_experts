from app.models import Olympiad, Criterion, SubCriterion, Aspect, Calculation, User, ExpertAssessment, Member, Role
from flask.ext.wtf import Form
from wtforms import SelectField, FormField, PasswordField
from wtforms_alchemy import model_form_factory, ModelFormField, ModelFieldList
from wtforms.validators import DataRequired
from app import db

ModelForm = model_form_factory(Form)


class MemberForm(ModelForm, Form):
    class Meta:
        # Добавить тайтл
        model = Member


class ExpertAssessmentForm(ModelForm, Form):
    class Meta:
        model = ExpertAssessment


class RoleForm(ModelForm, Form):
    class Meta:
        model = Role


class OlympiadAddForm(ModelForm, Form):
    class Meta:
        model = Olympiad
        date_format = '%d.%m.%Y'
        only = ['name', 'date', 'description', 'member_count']


class OlympiadEditForm(ModelForm, Form):
    class Meta:
        model = Olympiad
        date_format = '%d.%m.%Y'
        # хак, для правильного порядка
        only = ['name', 'date', 'description']

    # chief_expert = ModelFormField(label='Старший Эксперт', form_class=RoleForm)
    chief_expert = ModelFieldList(label='Старший Эксперт', unbound_field=FormField(RoleForm))
    experts = ModelFieldList(label='Эксперты', unbound_field=FormField(RoleForm))
    members = ModelFieldList(label='Участники', unbound_field=FormField(MemberForm))


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



