from app import flash


def flash_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Ошибка в поле %s - %s" %
                  (getattr(form, field).label.text, error),
                  'danger')


def flash_add(instance):
    flash('Добавлен объект: %s' % instance, 'info')


def flash_edit(instance):
    flash('Изменен объект: %s' % instance, 'info')


def flash_delete(instance):
    flash('Удален объект: %s' % instance, 'warning')


def flash_error(error):
    flash('Ошибка! %s' % error, 'info')
