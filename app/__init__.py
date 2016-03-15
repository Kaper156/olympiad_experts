from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_wtf.csrf import CsrfProtect
from flask.views import MethodView

app = Flask(__name__)
app.config.from_object('config.DevelopConfig')
# CsrfProtect(app)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# DataBase
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
from app import models

db.create_all()

# Create calculations from models.lists-of-methods
models.load_calculations()


# Authenticate module
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Forms
from app import forms

# Routing
from app import flashing
OBJECT_PER_PAGE = 5


breadcrumbs = [
    ('Главная', 'index'),
    ('Олимпиады', 'olympiads'),
]
from app import views
