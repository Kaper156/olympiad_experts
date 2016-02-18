from app import render_template, db, app, request, redirect, url_for, flash, abort
from app.models import Measurement, MeasurementType, Aspect
from app.forms import Editor, EditorOlympiad
from wtforms.ext.sqlalchemy.orm import model_form

@app.route('/test')
def test():
    mt_form = model_form(MeasurementType)
    m_form = model_form(Measurement)
    a_form = model_form(Aspect)

