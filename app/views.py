from app import render_template, db, app, request, redirect, url_for, flash, abort, jsonify, flash_errors
from app.models import Olympiad, Criterion, SubCriterion, Aspect, Measurement, MeasurementType
from app.models import User, Role, Privilege
from app.forms import OlympiadForm, MeasurementForm, AspectForm
from wtforms.ext.sqlalchemy.orm import model_form


@app.route('/')
@app.route('/olympiads', methods=['POST', 'GET'])
def olympiads():
    olympiads = list(db.session.query(Olympiad).all())
    form = OlympiadForm()
    if request.method == 'POST' and form.validate():
        olympiad = Olympiad(name=form.name.data,
                            date=form.date.data,
                            description=form.description.data)
        db.session.add(olympiad)
        db.session.commit()
        flash('Олимпиада добавлена! \n %s: %s' % (olympiad.id, olympiad.name), 'error')
    flash_errors(form)
    return render_template('olympiads.html', olympiads=olympiads, form=form)

@app.route('/olympiads/edit-<int:id>', methods=['POST'])
def edit_olympiads(id):
    Form = model_form(Olympiad, base_class=OlympiadForm, db_session=db.session)
    olympiad = db.session.query(Olympiad).get(id)
    form = Form(request.form, olympiad)
    if request.method == 'POST' and form.validate():
        form.populate_obj(olympiad)
        flash('Олимпиада измененна', 'success')
        return jsonify('success')
    else:
        print(form.name)
        print(form.date)
        print(form.description)
        json = dict([(field.name, field) for field in form])
        # return jsonify(json)
        return render_template('ajax_form.html', form=form)

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
