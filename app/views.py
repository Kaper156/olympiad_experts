from app import render_template, db, app, request, redirect, url_for, flash, abort
from app.models import Olympiad, Section, Task, SubTask, Criterion
from app.forms import Editor, EditorOlympiad
from wtforms.ext.sqlalchemy.orm import model_form


def flash_editor_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("В поле '%s'- ошибка: %s" % (
                getattr(form, field).label.text,
                error
            ))

@app.route('/add/olympiad', methods=['GET', 'POST'])
def add_olympiad():
    title = "Добавление олимпиады"
    form = EditorOlympiad()

    if form.validate_on_submit():
        new_olympiad = Olympiad(name=form.name.data,
                                max_balls=form.max_balls.data,
                                description=form.description.data)
        db.session.add(new_olympiad)
        db.session.commit()
        flash('Добавлена Олимпиада!')
        return redirect(url_for("hierarchy"))

    flash(flash_editor_errors(form))
    return render_template("editor.html", form=form, action='/add/olympiad', title=title)


def edit(OrmForm, model):
    form = OrmForm(request.form, model)
    if form.validate_on_submit():
        form.populate_obj(model)
        model.put()
        flash("MyModel updated")
        return redirect(url_for("index"))
    return render_template("editor.html", form=form)


@app.route('/edit/olympiad/<int:id>', methods=['GET', 'POST'])
def edit_olympiad(id):
    OlimpiadForm = model_form(Olympiad, exclude=['children'], base_class=EditorOlympiad)
    model = db.session.query(Olympiad).get(id)
    return edit(OlimpiadForm, model)


@app.route('/edit/section/<int:id>', methods=['GET', 'POST'])
def edit_section(id):
    SectionForm = model_form(Section, exclude=['children'], base_class=Editor)
    model = db.session.query(Section).get(id)
    return edit(SectionForm, model)


@app.route('/edit/task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    TaskForm = model_form(Task, exclude=['children'], base_class=Editor)
    model = db.session.query(Task).get(id)
    return edit(TaskForm, model)


@app.route('/view')
@app.route('/')
def hierarchy():
    olympiads = list(db.session.query(Olympiad).limit(5))
    print(olympiads)
    print(len(olympiads))
    return render_template('hierarchy.html', olympiads=olympiads)


@app.route('/test')
def test_add():
    from datetime import date

    # o = Olympiad(name='Test',
    #              description='Blabla' * 3,
    #              max_balls=float(520),
    #              # date=date(1990, 1, 12)
    #              )
    o = Olympiad('Name', 520.0, 'Bla-bla-bla\n'*5)
    db.session.add(o)
    db.session.commit()
    return '<a href="/view">Посмотерть!</a>'
