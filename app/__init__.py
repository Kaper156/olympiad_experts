from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_wtf.csrf import CsrfProtect
app = Flask(__name__)
app.config.from_object('config.DevelopConfig')
CsrfProtect(app)
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


from app import models
from app import forms
from app import views

db.create_all()
