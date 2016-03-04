from app import db
from sqlalchemy import Integer, String, Text, Float, Date
from sqlalchemy_defaults import make_lazy_configured, Column

make_lazy_configured(db.mapper)


# Абстрактный класс, хранит поля требуемые компонентам олимпиады
class OlympiadBase(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, label='Название', nullable=False)
    max_balls = Column(Float, label='Максимум баллов', nullable=False)


# Конкретное задание: Установить ОС Windows Xp
class Aspect(OlympiadBase):
    __tablename__ = 'Aspect'
    description = Column(Text, label='Описание')
    max_balls = Column(Float, nullable=False)

    sub_criterion_id = db.Column(db.Integer, db.ForeignKey('SubCriterion.id'))
    sub_criterion = db.relationship('SubCriterion', backref=db.backref('Aspect', lazy='dynamic'))

    calculation_id = db.Column(db.Integer, db.ForeignKey('Calculation.id'))
    Calculation = db.relationship('Calculation', backref=db.backref('Aspect', lazy='dynamic'))

    def __str__(self):
        return '<Модуль: "%s" (%s)>' % (self.name, self.max_balls)


# Хранит конкретные методы вычисления
class Calculation(db.Model):
    __tablename__ = 'Calculation'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    description = Column(String)
    # TODO хранить текст лямбда функций?+
    a = lambda a: a*2
    method = Column(Text)

    def calc(self, value):
        return self.method(value)


# Хранит набранные баллы участника за определенный аспект
class Measurement(db.Model):
    __tablename__ = 'Measurement'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    value = Column(Float, nullable=False)

    aspect_id = db.Column(db.Integer, db.ForeignKey('Aspect.id'))
    aspect = db.relationship('Aspect', backref=db.backref('Measurement', lazy='dynamic'))


# Часть привязанная к конкретной области: ОС Linux, Программирование на Python
class SubCriterion(OlympiadBase):
    __tablename__ = 'SubCriterion'
    criterion_id = db.Column(db.Integer, db.ForeignKey('Criterion.id'))
    criterion = db.relationship('Criterion', backref=db.backref('SubCriterion', lazy='dynamic'))

    def __str__(self):
        return '<Подмодуль: "%s" (%s)>' % (self.name, self.max_balls)


# Часть олимпиады: Настройка сетевого оборудования, etc
class Criterion(OlympiadBase):
    __tablename__ = 'Criterion'
    olympiad_id = db.Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad = db.relationship('Olympiad', backref=db.backref('Criterion', lazy='dynamic'))
    # max_balls = Column('Максимум баллов', Integer, )

    def __str__(self):
        return '<Модуль: "%s" (%s)>' % (self.name, self.max_balls)


# Мероприятие
class Olympiad(db.Model):
    __tablename__ = 'Olympiad'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, label='Название', nullable=False)
    date = Column(Date, label='Дата', nullable=False)
    description = Column(String, label='Описание')
    # Status?

    def __str__(self):
        return '<Олимпиада: "%s" от [%s]>' % (self.name, self.date)


# Этап олимпиады 
class Status(db.Model):
    # рано
    __tablename__ = 'Status'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)


# Права
class Privilege(db.Model):
    __tablename__ = 'Privilege'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    rights = Column('Уровень', Integer, nullable=False)


# Пользователь системы
class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    login = Column('Логин', String, nullable=False)
    password = Column('Пароль', String, nullable=False)


# Связь между пользователем, правами и олимпиадой
class Role(db.Model):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

    olympiad_id = db.Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad = db.relationship('Olympiad', backref=db.backref('Role', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    user = db.relationship('User', backref=db.backref('Role', lazy='dynamic'))

    privilege_id = db.Column(db.Integer, db.ForeignKey('Privilege.id'))
    privilege = db.relationship('Privilege', backref=db.backref('Role', lazy='dynamic'))
