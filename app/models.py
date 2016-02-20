from app import db
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Date
from sqlalchemy.orm import relationship


# Абстрактный класс, хранит поля требуемые компонентам олимпиады
class OlympiadBase(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    max_balls = Column(Float, nullable=False)
    name = Column(String, nullable=False)

    def __init__(self, name, max_balls):
        self.name = name
        self.max_balls = max_balls


# Конкретное задание: Установить ОС Windows Xp
class Aspect(OlympiadBase):
    __tablename__ = 'Aspect'
    # id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    # name = Column(String)
    description = Column(Text)
    measurements = relationship("Measurement")

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
    measurements = relationship("Measurement")

    def __init__(self, name, method, description=None):
        self.name = name
        self.method = method
        self.description = description


# Ссылается на метод вычисления и аспект
class Measurement(db.Model):
    __tablename__ = 'Measurement'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    max_balls = Column(Float, nullable=False)
    id_aspect = Column(Integer, ForeignKey('Aspect.id'))
    id_measurement_type = Column(Integer, ForeignKey('Measurement.id'))

    def __init__(self, max_balls, aspect, measurement):
        # TODO init from parent id, calc ball_limit = parent.balls - sum([parent.children.ball])
        self.max_balls = max_balls
        self.id_aspect = aspect
        self.id_measurement_type = measurement


# Часть привязанная к конкретной области: ОС Linux, Программирование на Python
class SubCriterion(OlympiadBase):
    __tablename__ = 'SubCriterion'
    id_criterion = Column(Integer, ForeignKey('Criterion.id'))
    aspects = relationship('Aspect')


# Часть олимпиады: Настройка сетевого оборудования, etc
class Criterion(OlympiadBase):
    __tablename__ = 'Criterion'
    id_olympiad = Column(Integer, ForeignKey('Olympiad.id'))
    subcriterion = relationship('SubCriterion.id')


# Мероприятие
class Olympiad(db.Model):
    __tablename__ = 'Olympiad'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String)
    criterion = relationship('Criterion')
    role = relationship('Role')

    def __init__(self, name, date, description=None):
        self.name = name
        self.date = date
        self.description = description


# Права
class Privilege(db.Model):
    __tablename__ = 'Privilege'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    rights = Column(String, nullable=False)
    role = relationship('Role')

    def __init__(self, name, rights):
        self.name = name
        self.rights = rights


# Пользователь системы
class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = relationship('Role')

    def __init__(self, login, password):
        self.login = login
        self.password = hash(password)


# Связь между пользователем, правами и олимпиадой
class Role(db.Model):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    id_user = Column(Integer, ForeignKey('User.id'))
    id_olympiad = Column(Integer, ForeignKey('Olympiad.id'))
    id_privilege = Column(Integer, ForeignKey('Privilege.id'))

    def __init__(self, user, olympiad, privilege):
        self.id_olympiad = olympiad
        self.id_user = user
        self.id_privilege = privilege
