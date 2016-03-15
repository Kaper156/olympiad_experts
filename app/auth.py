from functools import wraps
from app import request, Response, db
from app.models import User


def check_auth(login, password, privilege):
    """This function is called to check if a username /
    password combination is valid.
    """
    user = db.session.query(User).filter(User.login == login).first()
    if privilege:
        if user.privilege != privilege:
            return False
    try:
        return user.password == password
    except AttributeError:
        return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f, role=None):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password, role):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
