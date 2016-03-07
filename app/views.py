from app import render_template, db, app, request, redirect, url_for, MethodView, abort
from app import breadcrumbs, OBJECT_PER_PAGE
from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement, Calculation
from app.forms import OlympiadForm, CriterionForm, SubCriterionForm, AspectForm, CalculationForm
from app.flashing import flash_form_errors, flash_error, flash_add, flash_edit, flash_delete, flash_max_ball


class BaseView:

    def __init__(self, _class, _form, template_name, end_point=''):
        self.cls = _class
        self.form = _form
        self.template = template_name

        self.endpoint = end_point
        self.init_end_points()

    def init_end_points(self):
        app.add_url_rule('/%s/' % self.endpoint,
                         endpoint='%s' % self.endpoint,
                         view_func=self.all,
                         methods=['GET'])
        app.add_url_rule('/%s/add/' % self.endpoint,
                         endpoint='%s_add' % self.endpoint,
                         view_func=self.add,
                         methods=['POST'])
        app.add_url_rule('/%s/edit/<int:id>' % self.endpoint,
                         endpoint='%s_edit' % self.endpoint,
                         view_func=self.edit,
                         methods=['POST'])
        app.add_url_rule('/%s/delete/<int:id>' % self.endpoint,
                         endpoint='%s_delete' % self.endpoint,
                         view_func=self.delete,
                         methods=['POST'])

    def redirect(self):
        return redirect(self.endpoint)

    def all(self):
        results = list()
        for instance in db.session.query(self.cls).limit(OBJECT_PER_PAGE):
            results.append((instance, self.form(obj=instance)))

        # form to add new inst
        editor = self.form()
        return render_template(self.template, objects=results, form=editor)

    def edit(self, id):
        instance = db.session.query(self.cls).get(id)
        form = self.form(request.form, self.cls)
        if form.validate_on_submit():
            form.populate_obj(instance)
            db.session.commit()
            flash_edit(instance)
        else:
            flash_form_errors(form)
        return self.redirect()

    def add(self):
        form = self.form(request.form, self.cls)
        instance = self.cls()
        if form.validate_on_submit():
            form.populate_obj(instance)
            db.session.add(instance)
            db.session.commit()
            flash_add(instance)
        else:
            flash_form_errors(form)
        return self.redirect()

    def delete(self, id):
        instance = db.session.query(self.cls).get(id)
        db.session.query(self.cls).filter(self.cls.id == id).delete()
        flash_delete(instance)
        db.session.commit()
        return self.redirect()


class ChildAPI(BaseView):
    def __init__(self, _class, _form, template, end_point,
                 query_check_add=None, query_check_edit=None, query_maximum=lambda x:100):
        BaseView.__init__(self, _class, _form, template, end_point=end_point)
        self.query = dict()
        self.query['all'] = query_check_add
        self.query['edit'] = query_check_edit
        self.query['maximum_balls'] = query_maximum

    def init_end_points(self):
        app.add_url_rule('/%s-of-<int:parent_id>/' % self.endpoint,
                         endpoint='%s' % self.endpoint,
                         view_func=self.all,
                         methods=['GET'])
        app.add_url_rule('/%s-of-<int:parent_id>/add/' % self.endpoint,
                         endpoint='%s_add' % self.endpoint,
                         view_func=self.add,
                         methods=['POST'])
        app.add_url_rule('/%s-of-<int:parent_id>/edit/<int:id>' % self.endpoint,
                         endpoint='%s_edit' % self.endpoint,
                         view_func=self.edit,
                         methods=['POST'])
        app.add_url_rule('/%s-of-<int:parent_id>/delete/<int:id>' % self.endpoint,
                         endpoint='%s_delete' % self.endpoint,
                         view_func=self.delete,
                         methods=['POST'])

    def all(self, parent_id):
        results = list()
        for instance in self.query['all'](parent_id):
            results.append((instance, self.form(obj=instance)))
        maximum_balls = self.query['maximum_balls'](parent_id)
        # form to add new inst
        editor = self.form()
        return render_template(self.template, objects=results, form=editor, parent_id=parent_id, maximum_balls=maximum_balls)

    def edit(self, id, parent_id):

        instance = db.session.query(self.cls).get(id)
        form = self.form(request.form, self.cls)
        if form.validate_on_submit():
            received_balls = form.max_balls.data
            value = self.check_balls(instance.id, parent_id, received_balls, self.query['maximum_balls'](parent_id))
            if value == received_balls:
                form.populate_obj(instance)
                db.session.commit()
                flash_edit(instance)
            else:
                flash_max_ball(received_balls, value)
        else:
            flash_form_errors(form)
        return self.redirect()

    def add(self, parent_id):
        instance = self.cls()
        form = self.form(request.form, self.cls)
        if form.validate_on_submit():
            received_balls = form.max_balls.data
            value = self.check_balls(None, parent_id, received_balls, self.query['maximum_balls'](parent_id))
            if value == received_balls:
                form.populate_obj(instance)
                db.session.add(instance)
                db.session.commit()
                print(instance.id)
                flash_add(instance)
            else:
                flash_max_ball(received_balls, value)
        else:
            flash_form_errors(form)
        return self.redirect()

    def check_balls(self, _id, parent_id, new_value, maximum=100.0):
        _sum = 0.0

        if _id:
            query = self.query['edit'](_id, parent_id)
        else:
            query = self.query['all'](parent_id)

        for instance in query:
            _sum += instance.max_balls
        # todo change to reduce

        if _sum + new_value > maximum:
            new_value = maximum - _sum
        return new_value


class OlympiadView(BaseView):
    def __init__(self):
        BaseView.__init__(self, Olympiad, OlympiadForm, 'olympiad.html', end_point='olympiad')


class CriterionView(ChildAPI):
    def __init__(self):
        query_add  = lambda parent_id: db.session.query(Criterion).filter(Criterion.olympiad_id == parent_id)
        query_edit = lambda id, parent_id: db.session.query(Criterion).filter(Criterion.olympiad_id == parent_id).filter(Criterion.id != id)

        ChildAPI.__init__(self,
                          _class=Criterion,
                          _form=CriterionForm,
                          end_point='criterion',
                          template='criterion.html',
                          query_check_add=query_add,
                          query_check_edit=query_edit)


class SubCriterionView(ChildAPI):
    def __init__(self):
        query_add  = lambda parent_id: db.session.query(SubCriterion).filter(SubCriterion.criterion_id == parent_id)
        query_edit = lambda id, parent_id: db.session.query(SubCriterion).filter(SubCriterion.criterion_id == parent_id).filter(SubCriterion.id != id)
        query_max  = lambda parent_id: db.session.query(Criterion).get(parent_id).max_balls

        ChildAPI.__init__(self,
                          _class=Criterion,
                          _form=CriterionForm,
                          end_point='sub_criterion',
                          template='sub_criterion.html',
                          query_check_add=query_add,
                          query_maximum=query_max,
                          query_check_edit=query_edit)


class AspectView(ChildAPI):
    def __init__(self):
        query_add  = lambda parent_id: db.session.query(Aspect).filter(Aspect.sub_criterion_id == parent_id)
        query_edit = lambda id, parent_id: db.session.query(Aspect).filter(Aspect.sub_criterion_id == parent_id).filter(Aspect.id != id)
        query_max  = lambda parent_id: db.session.query(SubCriterion).get(parent_id).max_balls

        ChildAPI.__init__(self,
                          _class=Aspect,
                          _form=AspectForm,
                          end_point='aspect',
                          template='aspect.html',
                          query_check_add=query_add,
                          query_maximum=query_max,
                          query_check_edit=query_edit)


OlympiadView()
CriterionView()
SubCriterionView()
AspectView()
