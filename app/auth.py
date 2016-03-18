from functools import wraps
from app import request, db, abort, render_template, app, redirect, session, request, url_for
from app.models import User, Privilege, R_ADMIN, R_EXPERT
from app.forms import LoginForm
from app.flashing import flash_form_errors

privilege_admin = db.session.query(Privilege).filter(Privilege.rights == R_ADMIN).first()
privilege_expert = db.session.query(Privilege).filter(Privilege.rights == R_EXPERT).first()


def check_auth():
    privilege = session.pop('privilege', default=None)
    auth = LoginForm(request.form, User)
    if auth.validate_on_submit():
        new_user = User()
        if session.get('user'):
            new_user.login, new_user.password = session['user_login'], session['user_password']
        else:
            auth.populate_obj(new_user)
        user = db.session.query(User).filter(User.login == new_user.login).first()
        print(new_user)
        print(user)
        if user.password == new_user.password:
            if privilege is None:
                privilege = privilege_expert
            if user.privilege.rights >= privilege.rights:
                session['user_login'], session['user_password'] = user.login, user.password
                return True
            else:
                abort(401)

    flash_form_errors(auth)
    return False


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form, User)
    if check_auth():
        next_url = session.pop('next_url', '/')
        return redirect(next_url)
    return render_template('login.html', form=form)


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect('/')


def requires_user(f, privilege=privilege_expert):
    @wraps(f)
    def decorated(*args, **kwargs):
        session['privilege'] = privilege.id
        session['next_url'] = request.url
        return f(*args, **kwargs)
        if not check_auth():
            return redirect(url_for('login'))

    return decorated


def require_admin(f):
    return requires_user(f, privilege=privilege_admin)
