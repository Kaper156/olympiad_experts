from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_wtf.csrf import CsrfProtect

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


# Forms
from app import forms
import wtforms_json
wtforms_json.init()
from flask.json import JSONEncoder, dumps
from sqlalchemy.ext.declarative import DeclarativeMeta


# Routing
class MappedJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # обрабатываем объект sqlalchemy
            fields = dict()
            obj_dict = obj.__dict__
            for field in obj.__table__.columns.keys():  # получаем список полей связанной с моделью таблицы
                data = obj_dict.get(field)  # извлекаем данные по имени поля
                try:
                    dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
app.json_encoder = MappedJSONEncoder


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


breadcrumbs = [
    ('Главная', 'index'),
    ('Олимпиады', 'olympiads'),
]
from app import views
