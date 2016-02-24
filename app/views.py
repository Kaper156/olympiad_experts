from app import render_template, db, app, request, redirect, url_for, flash, abort, jsonify, flash_errors
from app import breadcrumbs
from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement, MeasurementType
from app.models import User, Role, Privilege
from app.forms import OlympiadForm, MeasurementForm, AspectForm
from wtforms.ext.sqlalchemy.orm import model_form


@app.route('/')
def index():
    return render_template('base.html', breadcrumbs=breadcrumbs[:1])


@app.route('/olympiads/', methods=['POST', 'GET'])
def olympiads():
    instances = list()
    for olympiad in db.session.query(Olympiad).all():
        inst_form = model_form(Olympiad,
                               base_class=OlympiadForm,
                               db_session=db.session,
                               exclude=['Role', 'Criterion'])
        instances.append((olympiad, inst_form(request.form, olympiad)))

    editor = OlympiadForm()
    if request.method == 'POST' and editor.validate():
        olympiad = Olympiad(name=editor.name.data,
                            date=editor.date.data,
                            description=editor.description.data)
        db.session.add(olympiad)
        db.session.commit()
        flash('Олимпиада добавлена! \n %s: %s' % (olympiad.id, olympiad.name), 'info')
    flash_errors(editor)
    return render_template('olympiads.html', breadcrumbs=breadcrumbs[:2], olympiads=instances, form=editor)


@app.route('/olympiads/edit-<int:id>', methods=['POST'])
def edit_olympiads(id):
    Form = model_form(Olympiad, base_class=OlympiadForm, db_session=db.session)
    olympiad = db.session.query(Olympiad).get(id)
    form = Form(request.form, Olympiad)
    if request.method == 'POST' and form.validate():
        form.populate_obj(olympiad)
        db.session.commit()
        flash('Олимпиада #%s: "%s" измененна' % (olympiad.id, olympiad.name), 'info')
    else:
        flash('Ошибка при изменении олимпиады', 'warning')
        flash_errors(form)
    return redirect(url_for('olympiads'))


@app.route('/olympiads/add', methods=['POST'])
def add_olympiad():
    form = OlympiadForm()
    if request.method == 'POST' and form.validate():
        olympiad = Olympiad(name=form.name.data,
                            date=form.date.data,
                            description=form.description.data)
        db.session.add(olympiad)
        db.session.commit()
        flash('Олимпиада #%s: "%s" добавлена! \n ' % (olympiad.id, olympiad.name), 'info')
    else:
        flash_errors(form)
    return redirect(url_for('olympiads'))


@app.route('/olympiads/delete-<int:id>', methods=['POST'])
def del_olympiad(id):
    olympiad = db.session.query(Olympiad).get(id)
    flash('Олимпиада #%s: "%s" удалена! \n ' % (olympiad.id, olympiad.name), 'warning')

    db.session.query(Olympiad).filter(Olympiad.id == id).delete()
    db.session.commit()
    return redirect(url_for('olympiads'))

