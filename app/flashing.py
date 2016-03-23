from app import flash


def flash_form_errors(form):
    field_errors = []
    for field, errors in form.errors.items():
        for error in errors:
            field_errors += "\n<li>Ошибка в поле %s - %s</li>" % (getattr(form, field).label.text, error)
    if len(field_errors):
        result = '<span>Ошибки при заполнении формы:</span><ul>'
        result += ''.join(field_errors)
        result += '\n</ul>'
        flash(result, 'danger')


def flash_add(instance):
    flash('Добавлен объект: %s' % instance, 'info')


def flash_edit(instance):
    flash('Изменен объект: %s' % instance, 'info')


def flash_delete(instance):
    flash('Удален объект: %s' % instance, 'warning')


def flash_error(error):
    flash('Ошибка! <br>\n%s' % error, 'warning')


def flash_max_ball(getted, needed):
    flash_error('Вы ввели недопустимое количество баллов: %s <br>\nМаксимально возможное: %s' % (getted, needed))


def flash_message(message):
    flash(message, 'info')
