from app import render_template, db, app, request, redirect, url_for, flash, abort
from app.models import Measurement, MeasurementType, Aspect
from app.forms import MeasurementForm, AspectForm
from wtforms.ext.sqlalchemy.orm import model_form

@app.route('/add/measurement')
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
