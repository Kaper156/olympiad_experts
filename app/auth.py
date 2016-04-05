from functools import wraps
from app import request, db, abort, render_template, app, redirect, session, request, url_for
from app.models import User, Privilege, R_ADMIN, R_EXPERT
from app.forms import LoginForm
from app.flashing import flash_form_errors, flash_error

privilege_admin = db.session.query(Privilege).filter(Privilege.rights == R_ADMIN).first()
privilege_expert = db.session.query(Privilege).filter(Privilege.rights == R_EXPERT).first()


# Показывать форму пока не залогинишься
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form, User())
    if form.is_submitted():
        incoming = User()
        form.populate_obj(incoming)
        if authenticate(incoming):
            next_url = '/'
            if authorize():
                next_url = session.pop('next_url', '/')
            return redirect(next_url)
    return render_template('login.html', form=form)


def authenticate(incoming):
    user = db.session.query(User).filter(User.login == incoming.login).first()
    if user and user.password == incoming.password:
        session['user'] = user.id
        session['user_login'] = user.login
        return True
    else:
        flash_error('Неверный Логин\\Пароль!')
    return False


def authorize():
    if session.get('user') and session.get('privilege'):
        privilege = db.session.query(Privilege).get(session.get('privilege'))
        user = db.session.query(User).get(session['user'])
        if user.privilege.rights >= privilege.rights:
            return True
        abort(502)
    return False


@app.route('/logout/')
def logout():
    session.pop('user', None)
    session.pop('user_login', None)
    return redirect('/')


def requires_user(f, privilege=privilege_expert):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
        if authorize():
            return f(*args, **kwargs)
        session['privilege'] = privilege.id
        session['next_url'] = request.url
        return redirect(url_for('login'))

    return decorated


def require_admin(f):
    return requires_user(f, privilege=privilege_admin)
