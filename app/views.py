from app import render_template, db, app, request, redirect, url_for, flash, abort, jsonify, flash_errors
from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement, MeasurementType
from app.models import User, Role, Privilege
from app.forms import OlympiadForm, MeasurementForm, AspectForm
from wtforms.ext.sqlalchemy.orm import model_form


@app.route('/')
@app.route('/olympiads', methods=['POST', 'GET'])
def olympiads():
    instances = list()
    for olympiad in db.session.query(Olympiad).all():
        inst_form = model_form(olympiad.__class__, base_class=OlympiadForm, db_session=db.session)
        instances.append((olympiad, inst_form(request.form, olympiad)))

    editor = OlympiadForm()
    if request.method == 'POST' and editor.validate():
        olympiad = Olympiad(name=editor.name.data,
                            date=editor.date.data,
                            description=editor.description.data)
        db.session.add(olympiad)
        db.session.commit()
        flash('Олимпиада добавлена! \n %s: %s' % (olympiad.id, olympiad.name), 'error')
    flash_errors(editor)
    return render_template('olympiads.html', olympiads=instances, form=editor)

@app.route('/olympiads/edit-<int:id>', methods=['POST', 'GET'])
def edit_olympiads(id):
    Form = model_form(Olympiad, base_class=OlympiadForm, db_session=db.session)
    olympiad = db.session.query(Olympiad).get(id)
    form = Form(request.form, Olympiad)
    if request.method == 'POST' and form.validate():
        form.populate_obj(olympiad)
        flash('Олимпиада измененна', 'success')
        return jsonify({'answer': True})
    return jsonify({'answer': False})

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

@app.route('/test')
def test():
    olympiads = (db.session.query(Olympiad).get(1))
    form = OlympiadForm()
    if request.method == 'POST' and form.validate():
        olympiad = Olympiad(name=form.name.data,
                            date=form.date.data,
                            description=form.description.data)
        db.session.add(olympiad)
        db.session.commit()
        flash('Олимпиада добавлена! \n %s: %s' % (olympiad.id, olympiad.name), 'error')
    flash_errors(form)
    return render_template('ajax_form.html', olympiad=olympiads, form=form)

@app.route('/add/measurement', methods=['POST'])
def add_measurement():
    Form = model_form(Measurement, MeasurementForm)
    form = Form(request.form)
    if form.validate():
        obj = Measurement(max_balls=form.max_balls.data, measurement=form.measurement_type.data)
        db.session.add(obj)
        return redirect(url_for('view_measurements', id=obj.id))
    return render_template('add_measurement.html')


@app.route('/view/measurement/<int:id>')
def view_measurements(id):

    obj = db.session.query(Measurement).filter(id=id)
    render_template('view_measurement.html', obj=obj)


@app.route('/view/aspect/<int:id>')
def view_aspects(id):
    if id == 0:
        aspects = db.session.query(Aspect).all()
        return render_template('view_aspects.html', aspects=aspects)
    obj = db.session.query(Measurement).filter(id=id)
    return render_template('view_aspects.html', obj=obj)
