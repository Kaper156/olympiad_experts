from functools import wraps
from app import request, db, abort, render_template, app, redirect, session, request, url_for
from app.models import User, Privilege, R_ADMIN, R_EXPERT
from app.forms import LoginForm
from app.flashing import flash_form_errors

privilege_admin = db.session.query(Privilege).filter(Privilege.rights == R_ADMIN).first()
privilege_expert = db.session.query(Privilege).filter(Privilege.rights == R_EXPERT).first()


# Показывать форму пока не залогинишься
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form, User)
    if form.is_submitted():
        incoming = User()
        form.populate_obj(incoming)
        validation = validate(incoming)

        # Вход
        if validation:
            # Проверка прав доступа к ресурсу
            if validation > 0:
                next_url = session.pop('next_url', '/')
            else:
                next_url = '/'
            return redirect(next_url)
    return render_template('login.html', form=form)


def validate(incoming):
    # incoming = User()
    # form.populate_obj(incoming)
    user = db.session.query(User).filter(User.login == incoming.login).first()
    if user and user.password == incoming.password:
        privilege = db.session.query(Privilege).get(session.get('privilege'))
        session['user'] = user.id
        if user.privilege.rights >= privilege.rights:
            return 1
        else:
            return -1
    return 0


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect('/')


# Проверить наличие в сессии
# Если нету- послать в логин форм
# Если есть- проверить права доступа
def requires_user(f, privilege=privilege_expert):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user'):
            user = db.session.query(User).get(session['user'])
            if user.privilege.rights >= privilege.rights:
                return f(*args, **kwargs)
            else:
                abort(502)
        else:
            session['privilege'] = privilege.id
            session['next_url'] = request.url
        return redirect(url_for('login'))

    return decorated


def require_admin(f):
    return requires_user(f, privilege=privilege_admin)
