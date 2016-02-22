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


@app.route('/olympiads/edit-<int:id>', methods=['POST'])
def edit_olympiads(id):
    Form = model_form(Olympiad, base_class=OlympiadForm, db_session=db.session)
    olympiad = db.session.query(Olympiad).get(id)
    form = Form(request.form, Olympiad)
    if request.method == 'POST' and form.validate():
        form.populate_obj(olympiad)
        db.session.commit()
        flash('Олимпиада измененна', 'success')
        # todo return flashed
        return jsonify({'answer': True})
    return jsonify({'answer': False})



@app.route('/ajax/get/olympiad_<int:id>')
def get_olympiad(id):
    return get_element(Olympiad, id)


def get_element(cls, id):
    print((db.session.query(cls).get(id)).__dict__)
    return jsonify(**db.session.query(cls).get(id).__dict__)

