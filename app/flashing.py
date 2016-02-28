from app import flash


def flash_form_errors(form):
    result = '<span>Ошибки при заполнении формы:</span><ul>'
    for field, errors in form.errors.items():
        for error in errors:
            result += "\n<li>Ошибка в поле %s - %s</li>" % (getattr(form, field).label.text, error)
    result += '\n</ul>'
    flash(result, 'danger')

def flash_add(instance):
    flash('Добавлен объект: %s' % instance, 'info')


def flash_edit(instance):
    flash('Изменен объект: %s' % instance, 'info')


def flash_delete(instance):
    flash('Удален объект: %s' % instance, 'warning')


def flash_error(error):
    flash('Ошибка! %s' % error, 'info')
