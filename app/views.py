from app import render_template, db, app, request, redirect, url_for, MethodView, abort, login_manager
from app import breadcrumbs, OBJECT_PER_PAGE, jsonify
from app.models import Olympiad, Criterion, SubCriterion, Aspect, Calculation, User
from app.forms import OlympiadForm, CriterionForm, SubCriterionForm, AspectForm, CalculationForm, LoginForm
from app.flashing import flash_form_errors, flash_add, flash_edit, flash_delete, flash_max_ball, \
                         flash_message, flash_error


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

    def redirect(self, **kwargs):
        return redirect(url_for(self.endpoint, **kwargs))

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


class ChildView(BaseView):
    def __init__(self, _class, _form, template_name, end_point, parent_cls, query_maximum=lambda x: 100):
        BaseView.__init__(self, _class, _form, template_name, end_point=end_point)
        self.parent_cls = parent_cls
        self.query = dict()
        self.query['all'] = lambda parent_id: db.session.query(self.cls).filter(self.cls.parent_id == parent_id)
        self.query['edit'] = lambda id, parent_id: db.session.query(self.cls).filter(
            self.cls.parent_id == parent_id).filter(self.cls.id != id)
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

    def create_form(self):
        return self.form(request.form, self.cls)

    def all(self, parent_id):
        results = list()
        for instance in self.query['all'](parent_id):
            results.append((instance, self.form(obj=instance)))
        # form to add new inst
        editor = self.form()

        parent = db.session.query(self.parent_cls).get(parent_id)
        return render_template(self.template,
                               objects=results,
                               form=editor,
                               parent_id=parent_id,
                               parent=parent)

    def edit(self, id, parent_id):

        instance = db.session.query(self.cls).get(id)
        form = self.create_form()
        if form.validate_on_submit():
            received_balls = form.max_balls.data
            value = self.check_balls(instance.id, parent_id, received_balls, self.query['maximum_balls'](parent_id))
            if value == received_balls:
                instance.parent_id = parent_id
                form.populate_obj(instance)
                db.session.commit()
                flash_edit(instance)
            else:
                flash_max_ball(received_balls, value)
        else:
            flash_form_errors(form)
        return self.redirect(parent_id=parent_id)

    def add(self, parent_id):
        instance = self.cls()
        form = self.create_form()
        if form.validate_on_submit():
            received_balls = form.max_balls.data
            value = self.check_balls(None, parent_id, received_balls, self.query['maximum_balls'](parent_id))
            if value == received_balls:
                form.populate_obj(instance)
                db.session.add(instance)
                instance.parent_id = parent_id
                db.session.commit()
                print(instance.id)
                flash_add(instance)
            else:
                flash_max_ball(received_balls, value)
        else:
            flash_form_errors(form)
        return self.redirect(parent_id=parent_id)

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

    def delete(self, id, parent_id):
        instance = db.session.query(self.cls).get(id)
        # parent_id = instance.parent_id
        db.session.query(self.cls).filter(self.cls.id == id).delete()
        flash_delete(instance)
        db.session.commit()
        return self.redirect(parent_id=parent_id)


olympiad_view = BaseView(_class=Olympiad,
                         _form=OlympiadForm,
                         template_name='editors/olympiad.html',
                         end_point='olympiad')

criterion_view = ChildView(_class=Criterion,
                           _form=CriterionForm,
                           template_name='editors/criterion.html',
                           end_point='criterion',
                           parent_cls=Olympiad)

sub_criterion_view = ChildView(_class=SubCriterion,
                               _form=SubCriterionForm,
                               template_name='editors/sub_criterion.html',
                               end_point='sub_criterion',
                               query_maximum=lambda parent_id: db.session.query(Criterion).get(parent_id).max_balls,
                               parent_cls=Criterion)


aspect_view = ChildView(_class=Aspect,
                        _form=AspectForm,
                        template_name='editors/aspect.html',
                        end_point='aspect',
                        query_maximum=lambda parent_id: db.session.query(SubCriterion).get(parent_id).max_balls,
                        parent_cls=SubCriterion)


@app.route('/')
def index():
    return redirect('olympiad')


@app.route('/view_olympiads/')
def view_olympiads():
    # hierarchy = dict()
    # query = db.session.query(Olympiad).all()
    # classes = [Criterion, SubCriterion, Aspect]
    # for olympiad in query:
    #     hierarchy[olympiad] = recursive_hierarchy(classes, olympiad.id)
    return render_template('view_olympiad.html', hierarchy=hierarchy)


def recursive_hierarchy(classes, parent_id):
    result = dict()
    try:
        cls = classes.pop(0)
        query = db.session.query(cls).filter(cls.parent_id == parent_id).all()
        for instance in query or []:
            result[instance] = dict(recursive_hierarchy(classes, instance.id))
        return result
    except IndexError:
        return result
    except TypeError:
        return result

hierarchy = dict()
query = db.session.query(Olympiad).all()
classes = [Criterion, SubCriterion, Aspect]
for olympiad in query:
    hierarchy[olympiad] = recursive_hierarchy(classes, olympiad.id)


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return db.session.query(User).get(user_id) or None


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User()
        form.populate_object(user)
        if login_user(user):
            flash_message('Вы успешно вошли.')

            next = request.args.get('next')
            # next_is_valid should check if the user has valid
            # permission to access the `next` url
            # if not next_is_valid(next):
            #     return flask.abort(400)

            return redirect(next or url_for('index'))
        else:
            flash_error('Логин или пароль не подходит')
    return render_template('login.html', form=form)


def login_user(user):
    query = db.session.query(User).filter(User.login == user.login)
    # TODO Add to session
    if query.count() > 0 and query.password == user.password:
        return True
    return False
