from app import render_template, db, app, request, redirect, url_for
from app import breadcrumbs, OBJECT_PER_PAGE
from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement, MeasurementType
from app.models import User, Role, Privilege
from app.forms import OlympiadForm, CriterionForm
from app.flashing import flash, flash_form_errors, flash_error, flash_add, flash_edit, flash_delete
from wtforms.ext.sqlalchemy.orm import model_form


# UNIFICATED ADD, DELETE, EDIT instances
def add_instance(_class, _form):
    instance = _class()
    form = _form(request.form)
    if form.validate_on_submit():
        form.populate_obj(instance)
        db.session.add(instance)
        db.session.commit()
        flash_add(instance)
    else:
        flash_form_errors(form)


def edit_instance(_class, _form, _id):
    instance = db.session.query(_class).get(_id)
    form = _form(request.form, _class)
    if request.method == 'POST' and form.validate():
        form.populate_obj(instance)
        db.session.commit()
        flash_edit(instance)
    else:
        flash_form_errors(form)


def del_instance(_class, _id):
    instance = db.session.query(_class).get(_id)
    db.session.query(_class).filter(_class.id == _id).delete()
    flash_delete(instance)
    db.session.commit()


@app.route('/')
def index():
    return render_template('base.html', breadcrumbs=breadcrumbs[:1])


# Olympiads pages
@app.route('/olympiads/', methods=['POST', 'GET'])
def olympiads():

    # list of all objects on page
    instances = list()
    olympiads = db.session.query(Olympiad).limit(OBJECT_PER_PAGE)
    for olympiad in olympiads:
        instances.append((olympiad, OlympiadForm(obj=olympiad)))

    # form to add new inst
    editor = OlympiadForm()

    return render_template('olympiad.html', breadcrumbs=breadcrumbs[:2], olympiads=instances, form=editor)


@app.route('/olympiads/add', methods=['POST'])
def add_olympiad():
    add_instance(_class=Olympiad, _form=OlympiadForm)
    return redirect(url_for('olympiads'))


@app.route('/olympiad-<int:id>/edit', methods=['POST'])
def edit_olympiad(id):
    edit_instance(_class=Olympiad, _form=OlympiadForm, _id=id)
    return redirect(url_for('olympiads'))


@app.route('/olympiad-<int:id>/delete', methods=['POST'])
def del_olympiad(id):
    del_instance(_class=Olympiad, _id=id)
    return redirect(url_for('olympiads'))


# Criterion pages
@app.route('/olympiad-<int:olympiad_id>/criterion')
def criteria(olympiad_id):

    instances = list()
    criteria = db.session.query(Criterion).filter(Criterion.olympiad_id == olympiad_id).limit(OBJECT_PER_PAGE)
    for criterion in criteria:
        inst_form = model_form(Criterion,
                               base_class=CriterionForm,
                               db_session=db.session,)

        instances.append((criterion, inst_form(request.form, criterion)))

    editor = OlympiadForm()
    if request.method == 'POST' and editor.validate():
        olympiad = Olympiad(name=editor.name.data,
                            date=editor.date.data,
                            description=editor.description.data)
        db.session.add(olympiad)
        db.session.commit()
        flash('Олимпиада добавлена! \n %s: %s' % (olympiad.id, olympiad.name), 'info')
    flash_form_errors(editor)

    return render_template('criterion.html')
