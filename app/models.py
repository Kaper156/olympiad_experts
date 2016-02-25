from app import db
from sqlalchemy import Integer, String, Text, Float, Date
from sqlalchemy_defaults import make_lazy_configured, Column
from wtforms.validators import Optional
make_lazy_configured(db.mapper)


# Абстрактный класс, хранит поля требуемые компонентам олимпиады
class OlympiadBase(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, label='Название', nullable=False)
    max_balls = Column(Float, label='Максимум баллов', nullable=False)

    def __init__(self, name, max_balls):
        self.name = name
        self.max_balls = max_balls


# Конкретное задание: Установить ОС Windows Xp
class Aspect(OlympiadBase):
    __tablename__ = 'Aspect'
    description = Column(Text, label='Описание', )
    sub_criterion_id = db.Column(db.Integer, db.ForeignKey('SubCriterion.id'))
    sub_criterion = db.relationship('SubCriterion', backref=db.backref('Aspect', lazy='dynamic'))

    def __init__(self, name, max_balls=0, description=None):
        OlympiadBase.__init__(self, name, max_balls)
        self.description = description


# Хранит конкретные методы вычисления
class MeasurementType(db.Model):
    __tablename__ = 'MeasurementType'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    description = Column(String)
    # TODO хранить текст лямбда функций?
    method = Column(Text)

    def __init__(self, name, method, description=None):
        self.name = name
        self.method = method
        self.description = description


# Ссылается на метод вычисления и аспект
class Measurement(db.Model):
    __tablename__ = 'Measurement'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    max_balls = Column(Float, nullable=False)

    aspect_id = db.Column(db.Integer, db.ForeignKey('Aspect.id'))
    aspect = db.relationship('Aspect', backref=db.backref('Measurement', lazy='dynamic'))
    measurement_type_id = db.Column(db.Integer, db.ForeignKey('MeasurementType.id'))
    measurement_type = db.relationship('MeasurementType', backref=db.backref('Measurement', lazy='dynamic'))

    def __init__(self, max_balls, aspect, measurement):
        # TODO init from parent id, calc ball_limit = parent.balls - sum([parent.children.ball])
        self.max_balls = max_balls
        self.id_aspect = aspect
        self.id_measurement_type = measurement


# Часть привязанная к конкретной области: ОС Linux, Программирование на Python
class SubCriterion(OlympiadBase):
    __tablename__ = 'SubCriterion'
    criterion_id = db.Column(db.Integer, db.ForeignKey('Criterion.id'))
    criterion = db.relationship('Criterion', backref=db.backref('SubCriterion', lazy='dynamic'))


# Часть олимпиады: Настройка сетевого оборудования, etc
class Criterion(OlympiadBase):
    __tablename__ = 'Criterion'
    olympiad_id = db.Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad = db.relationship('Olympiad', backref=db.backref('Criterion', lazy='dynamic'))


# Мероприятие
class Olympiad(db.Model):
    __tablename__ = 'Olympiad'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, label='Название', nullable=False)
    date = Column(Date, label='Дата', nullable=False)
    description = Column(String, label='Описание')

    def __init__(self, name, date, description=None):
        self.name = name
        self.date = date
        self.description = description


# Этап олимпиады
class Status(db.Model):
    __tablename__ = 'Status'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)


# Права
class Privilege(db.Model):
    __tablename__ = 'Privilege'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    rights = Column('Уровень', Integer, nullable=False)

    def __init__(self, name, rights):
        self.name = name
        self.rights = rights


# Пользователь системы
class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    login = Column('Логин', String, nullable=False)
    password = Column('Пароль', String, nullable=False)

    def __init__(self, login, password):
        self.login = login
        self.password = hash(password)


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

    def __init__(self, user, olympiad, privilege):
        self.id_olympiad = olympiad
        self.id_user = user
        self.id_privilege = privilege
