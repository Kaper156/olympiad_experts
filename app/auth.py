from functools import wraps
from app import request, Response, db, abort
from app.models import User, Privilege, R_ADMIN, R_EXPERT
from app.flashing import flash_error

privilege_admin = db.session.query(Privilege).filter(Privilege.rights == R_ADMIN).first()
privilege_expert = db.session.query(Privilege).filter(Privilege.rights == R_EXPERT).first()


def check_auth(login, password, privilege):
    user = db.session.query(User).filter(User.login == login).first()
    if user.password == password:
        # OR rights?
        if user.privilege.rights >= privilege.rights:
            return True
        else:
            abort(401)
    return False


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_user(f, privilege=privilege_expert):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password, privilege):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    return requires_user(f, privilege=privilege_admin)
