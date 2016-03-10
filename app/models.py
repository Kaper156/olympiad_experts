from app import db
from sqlalchemy import Integer, String, Text, Float, Date, Boolean
from sqlalchemy_defaults import make_lazy_configured, Column

make_lazy_configured(db.mapper)


# Абстрактный класс, хранит поля требуемые компонентам олимпиады
class OlympiadBase(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, label='Название', nullable=False)
    max_balls = Column(Float, label='Максимум баллов', nullable=False)


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


# Часть олимпиады: Настройка сетевого оборудования, etc
class Criterion(OlympiadBase):
    __tablename__ = 'Criterion'
    parent_id = db.Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad = db.relationship('Olympiad', backref=db.backref('Criterion', lazy='dynamic'))
    # max_balls = Column('Максимум баллов', Integer, )

    def __str__(self):
        return '<Модуль: "%s" (%s)>' % (self.name, self.max_balls)


# Часть привязанная к конкретной области: ОС Linux, Программирование на Python
class SubCriterion(OlympiadBase):
    __tablename__ = 'SubCriterion'
    parent_id = db.Column(db.Integer, db.ForeignKey('Criterion.id'))
    criterion = db.relationship('Criterion', backref=db.backref('SubCriterion', lazy='dynamic'))

    def __str__(self):
        return '<Подмодуль: "%s" (%s)>' % (self.name, self.max_balls)


# Конкретное задание: Установить ОС Windows Xp
# Может быть объективным - по факту наличия и др.
# Или субъективным, оценки экспертов могут быть различными
class Aspect(OlympiadBase):
    __tablename__ = 'Aspect'
    description = Column(Text, label='Описание')

    parent_id = db.Column(db.Integer, db.ForeignKey('SubCriterion.id'))
    sub_criterion = db.relationship('SubCriterion', backref=db.backref('Aspect', lazy='dynamic'))

    calculation_id = db.Column(db.Integer, db.ForeignKey('Calculation.id'))
    calculation = db.relationship('Calculation', backref=db.backref('Aspect', lazy='dynamic'))

    def __str__(self):
        return '<Критерий: "%s" (%s)>' % (self.name, self.max_balls)

subjective_methods = [
    ('Шкала 10', 'lambda x: 1')
]
objective_methods = [
    ('Наличие', 'lambda x: bool(x)'),
    ('Диапозон-5', 'lambda x: x//5'),
    ('Диапозон-10', 'lambda x: x//10'),
]


# Хранит конкретные методы вычисления
# Например: диапозон, точно значение, да\нет и т.д.
class Calculation(db.Model):
    __tablename__ = 'Calculation'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, label='Название', nullable=False)
    description = Column(String, label='Описание', nullable=True)
    # TODO хранить текст лямбда функций?+
    content = Column(Text, nullable=False)
    is_subjective = Column(Boolean, nullable=False, default=True)

    # Получает категорию и идентификатор метода
    # Сохраняет в объект текст лямбда-функции
    def __init__(self, is_subjective, content, name, description=None):
        self.content = content
        self.name = name
        self.is_subjective = is_subjective
        if is_subjective:
            self.name = 'Субъективный:%s' % self.name
        else:
            self.name = 'Объективный:%s' % self.name
        if description:
            self.description = description

    def calc(self, assessment, max_ball):
        method = eval(self.content)
        return method(assessment)*max_ball

    def __str__(self):
        if self.description:
            return '<Метод: "%s" [%s] (%s)>' % (self.name, self.content, self.description)
        return '<Метод: "%s" [%s]>' % (self.name, self.content)


# Участник, связь всех оценок за аспекты и олимпиады
class Member(db.Model):
    __tablename__ = 'Member'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(Text, nullable=False, default="Участник")

    olympiad_id = db.Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad = db.relationship('Olympiad', backref=db.backref('Member', lazy='dynamic'))

    def __init__(self, olympiad_id):
        self.olympiad_id = olympiad_id
        self.name = "Участник #%d" % self.id

    def get_results(self):
        result = []

        assessments = db.session.query(MemberAssessment).filter(MemberAssessment.member_id == self.id)
        for assessment in assessments:
            # TODO (если не собран балл за аспект)
            if not assessment.ball:
                assessment.calc()
                db.session.commit()

            aspect = db.session.query(Aspect).get(assessment.aspect_id)
            result.append((aspect, assessment))
        return result


# Балл за конкретный аспект, вычисленная из оценок экспертов
class MemberAssessment(db.Model):
    __tablename__ = 'MemberAssessment'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

    member_id = db.Column(db.Integer, db.ForeignKey('Member.id'))
    member = db.relationship('Member', backref=db.backref('MemberAssessment', lazy='dynamic'))
    ball = Column(Integer, nullable=False)

    aspect_id = db.Column(db.Integer, db.ForeignKey('Aspect.id'))
    aspect = db.relationship('Aspect', backref=db.backref('MemberAssessment', lazy='dynamic'))

    def calc(self):
        """
        Расчитывает балл участника за конкретный критерий
        :return:
        """
        result = []
        expert_assessments = db.session.query(ExpertAssessment).filter(ExpertAssessment.member_assessment_id == self.id)
        for assessment in expert_assessments:
            result.append(assessment.ball)
        self.ball = self.aspect.calculation.calc(result)
        return self.ball


# Оценка эксперта за аспект
class ExpertAssessment(db.Model):
    __tablename__ = 'ExpertAssessment'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    assessment = Column(Float, label='Оценка', nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('Role.id'))
    role = db.relationship('Role', backref=db.backref('ExpertAssessment', lazy='dynamic'))

    member_assessment_id = db.Column(db.Integer, db.ForeignKey('MemberAssessment.id'))
    member_assessment = db.relationship('MemberAssessment', backref=db.backref('ExpertAssessment', lazy='dynamic'))


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
