from app import render_template, db, app, request, redirect, url_for
from app import breadcrumbs, OBJECT_PER_PAGE
from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement, MeasurementType
from app.models import User, Role, Privilege
from app.forms import OlympiadForm, CriterionForm
from app.flashing import flash, flash_form_errors, flash_error, flash_add, flash_edit, flash_delete
from wtforms.ext.sqlalchemy.orm import model_form


# UNIFICATED ADD, DELETE, EDIT instances
def get_all_instance(_class, _form, instances=None):
    result = list()
    for instance in instances or db.session.query(_class).limit(OBJECT_PER_PAGE):
        result.append((instance, _form(obj=instance)))

    # form to add new inst
    editor = _form()
    return editor, result


def add_instance(_class, _form, init_args={}):
    instance = _class(**init_args)
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
    editor, instances = get_all_instance(_class=Olympiad, _form=OlympiadForm)
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
@app.route('/olympiad-<int:olympiad_id>/criteria')
def criteria(olympiad_id):
    instances = db.session.query(Criterion).filter(Criterion.olympiad_id == olympiad_id)
    editor, criteria = get_all_instance(_class=Criterion, _form=CriterionForm, instances=instances)
    return render_template('criterion.html', form=editor, criteria=criteria, olympiad_id=olympiad_id)


@app.route('/olympiad-<int:olympiad_id>/criteria/add', methods=['POST'])
def add_criterion(olympiad_id):
    add_instance(_class=Criterion, _form=CriterionForm, init_args={'olympiad_id': olympiad_id})
    return redirect(url_for('criteria', olympiad_id=olympiad_id))


@app.route('/olympiad-<int:olympiad_id>/criterion-<int:criterion_id>/edit', methods=['POST'])
def edit_criterion(olympiad_id, criterion_id):
    edit_instance(_class=Criterion, _form=CriterionForm, _id=criterion_id)
    return redirect(url_for('criteria', olympiad_id=olympiad_id))


@app.route('/olympiad-<int:olympiad_id>/criterion-<int:criterion_id>/delete', methods=['POST'])
def del_criterion(olympiad_id, criterion_id):
    del_instance(_class=Criterion, _id=criterion_id)
    return redirect(url_for('criteria'))
