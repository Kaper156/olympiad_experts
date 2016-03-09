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
from app.models import Calculation, objective_methods, subjective_methods
if db.session.query(Calculation).count() == 0:
    for name, content in objective_methods:
        instance = Calculation(is_subjective=False,
                               content=content,
                               name=name)
        db.session.add(instance)
    for name, content in subjective_methods:
        instance = Calculation(is_subjective=True,
                               content=content,
                               name=name)
        db.session.add(instance)
    db.session.commit()




# Forms
from app import forms
import wtforms_json

wtforms_json.init()

# Routing
from app import flashing
OBJECT_PER_PAGE = 5


breadcrumbs = [
    ('Главная', 'index'),
    ('Олимпиады', 'olympiads'),
]
from app import views
