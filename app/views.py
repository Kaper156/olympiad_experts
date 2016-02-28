from app import render_template, db, app, request, redirect, url_for, jsonify
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


def get_all_instances(_class):
    return list(db.session.query(_class).limit(OBJECT_PER_PAGE))


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
    return instance


def edit_instance(_class, _form, _id, data=None):
    instance = db.session.query(_class).get(_id)
    form = _form(data or request.form, _class)
    if request.method == 'POST' and form.validate():
        form.populate_obj(instance)
        db.session.commit()
        flash_edit(instance)
    else:
        flash_form_errors(form)
    return instance


def del_instance(_class, _id):
    instance = db.session.query(_class).get(_id)
    db.session.query(_class).filter(_class.id == _id).delete()
    flash_delete(instance)
    db.session.commit()


def check_instance(query, value, maximum=100):
    wrong = False
    _sum = 0

    for instance in query:
        _sum += instance.max_balls
    # todo change to reduce

    if _sum + value > maximum:
        # Если значение преышает допустимый порог баллов
        # то вернуть максимально возможное количество баллов
        wrong = True
        value = maximum - _sum
    return jsonify(**{'wrong': wrong,
                      'result': float(value)})


@app.route('/')
def index():
    return render_template('base.html', breadcrumbs=breadcrumbs[:1])


# Olympiads pages
@app.route('/olympiads/', methods=['POST', 'GET'])
def olympiads():
    editor, instances = get_all_instance(_class=Olympiad, _form=OlympiadForm)
    return render_template('olympiad.html', breadcrumbs=breadcrumbs[:2], olympiads=instances, form=editor)


@app.route('/olympiads/add', methods=['POST'])
def olympiad_add():
    add_instance(_class=Olympiad, _form=OlympiadForm)
    return redirect(url_for('olympiads'))


@app.route('/olympiad-<int:id>/edit', methods=['POST'])
def olympiad_edit(id):
    edit_instance(_class=Olympiad, _form=OlympiadForm, _id=id)
    return redirect(url_for('olympiads'))


@app.route('/olympiad-<int:id>/delete', methods=['POST'])
def olympiad_del(id):
    del_instance(_class=Olympiad, _id=id)
    return redirect(url_for('olympiads'))


# Criterion pages
@app.route('/olympiad-<int:olympiad_id>/criteria')
def criteria(olympiad_id):
    instances = db.session.query(Criterion).filter(Criterion.olympiad_id == olympiad_id)
    editor, criteria = get_all_instance(_class=Criterion, _form=CriterionForm, instances=instances)
    return render_template('criterion.html', form=editor, criteria=criteria, olympiad_id=olympiad_id)


@app.route('/olympiad-<int:olympiad_id>/criteria/add', methods=['POST'])
def criterion_add(olympiad_id):
    add_instance(_class=Criterion, _form=CriterionForm, init_args={'olympiad_id': olympiad_id})
    return redirect(url_for('criteria', olympiad_id=olympiad_id))


@app.route('/criterion-<id>/edit', methods=['POST'])
def criterion_edit(id):
    new_instance = edit_instance(_class=Criterion, _form=CriterionForm, _id=id)
    return redirect(url_for('criteria', olympiad_id=new_instance.olympiad_id))


@app.route('/olympiad-<int:olympiad_id>/criterion-<id>/delete', methods=['POST'])
def criterion_del(olympiad_id, id):
    del_instance(_class=Criterion, _id=id)
    return redirect(url_for('criteria', olympiad_id=olympiad_id))


@app.route('/olympiad-<int:olympiad_id>/criterion-<id>/check-<int:value>', methods=['POST', 'GET'])
def criterion_check(olympiad_id, value, id):
    query = db.session.query(Criterion).filter(Criterion.olympiad_id == olympiad_id).filter(Criterion.id != id)
    return check_instance(query=query, value=value)
