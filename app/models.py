from app import db
# from sqlalchemy import Integer, String, Text, Float, Date, Boolean
from sqlalchemy_defaults import make_lazy_configured, Column

make_lazy_configured(db.mapper)

# Списки методов
subjective_methods = [
    ('Шкала 10', 'lambda x: 1')
]
objective_methods = [
    ('Наличие', 'lambda x: bool(x)'),
    ('Диапозон-5', 'lambda x: x//5'),
    ('Диапозон-10', 'lambda x: x//10'),
]

# Константы прав, используются для создания пользователей
R_ADMIN = 2
R_EXPERT = 1
R_GUEST = 0


# Права
class Privilege(db.Model):
    __tablename__ = 'Privilege'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(db.String, nullable=False)
    rights = Column('Уровень доступа', db.Integer, nullable=False)


def load_privilege():
    if db.session.query(Privilege).count() == 0:
        for name, rights in [('Гость', R_GUEST),
                             ('Эксперт', R_EXPERT),
                             ('Администратор', R_ADMIN)]:
            privilege = Privilege()
            privilege.name = name
            privilege.rights = rights
            db.session.add(privilege)
        db.session.commit()


# Пользователь системы
class User(db.Model):
    __tablename__ = 'User'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    login = Column(db.String, label='Логин', nullable=False)
    password = Column(db.String, label='Пароль', nullable=False)

    privilege_id = db.Column(db.Integer, db.ForeignKey('Privilege.id'))
    privilege = db.relationship('Privilege', backref=db.backref('User', lazy='dynamic'))



def load_users():
    if db.session.query(User).count() == 0:
        query = db.session.query(Privilege)
        privilege_admin = query.filter(Privilege.rights == R_ADMIN).first()
        privilege_expert = query.filter(Privilege.rights == R_EXPERT).first()
        users = [('Expert1', privilege_expert),
                 ('Expert2', privilege_expert),
                 ('Expert3', privilege_expert),
                 ('Expert4', privilege_expert),
                 ('Expert5', privilege_expert),
                 ('Admin', privilege_admin)]
        from os import urandom
        for login, privilege in users:
            user = User()
            user.login = login
            user.password = login
            user.privilege_id = privilege.id
            db.session.add(user)
        db.session.commit()


def reload_users():
    from os import urandom
    query = db.session.query(User).all()
    for user in query:
        # user = User()
        if user.privilege.rights < R_ADMIN:
            user.password = urandom(9)
    db.session.commit()


def write_users_credential():
    query = db.session.query(User).all()
    for user in query:
        if user.privilege.rights < R_ADMIN:
            with open('%s-%s.txt' % (user.privilege.rights, user.name), 'wt') as file:
                file.write('%s\n%s\n%s\n' % (user.privilege.name, user.name, user.password))


# Абстрактный класс, хранит поля требуемые компонентам олимпиады
class OlympiadBase(db.Model):
    __abstract__ = True
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(db.String, label='Название', nullable=False)
    max_balls = Column(db.Float, label='Максимум баллов', nullable=False)


# Мероприятие
class Olympiad(db.Model):
    __tablename__ = 'Olympiad'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(db.String, label='Название', nullable=False)
    date = Column(db.Date, label='Дата', nullable=False)
    description = Column(db.String, label='Описание')
    # Status?

    def __str__(self):
        return '<Олимпиада: "%s" от [%s]>' % (self.name, self.date)


# Часть олимпиады: Настройка сетевого оборудования, etc
class Criterion(OlympiadBase):
    __tablename__ = 'Criterion'
    parent_id = Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad = db.relationship('Olympiad', backref=db.backref('Criterion', lazy='dynamic'))

    def __str__(self):
        return '<Модуль: "%s" (%s)>' % (self.name, self.max_balls)


# Часть привязанная к конкретной области: ОС Linux, Программирование на Python
class SubCriterion(OlympiadBase):
    __tablename__ = 'SubCriterion'
    parent_id = Column(db.Integer, db.ForeignKey('Criterion.id'))
    criterion = db.relationship('Criterion', backref=db.backref('SubCriterion', lazy='dynamic'))

    def __str__(self):
        return '<Подмодуль: "%s" (%s)>' % (self.name, self.max_balls)


# Хранит конкретные методы вычисления
# Например: диапозон, точно значение, да\нет и т.д.
class Calculation(db.Model):
    __tablename__ = 'Calculation'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(db.String, label='Название', nullable=False)
    description = Column(db.String, label='Описание', nullable=True)
    content = Column(db.Text, nullable=False)
    is_subjective = Column(db.Boolean, nullable=False, default=True)

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


# Загрузить методы вычисления
def load_calculations():
    if db.session.query(Calculation).count() == 0:
        for name, content in objective_methods:
            instance = Calculation(is_subjective=False,
                                   content=content,
                                   name=name)
            db.session.add(instance)
        for name, content in subjective_methods:
            instance = Calculation(is_subjective=True,
                                   content=content,
                                   name=name)
            db.session.add(instance)
        db.session.commit()


# Конкретное задание: Установить ОС Windows Xp
# Может быть объективным - по факту наличия и др.
# Или субъективным, оценки экспертов могут быть различными
class Aspect(OlympiadBase):
    __tablename__ = 'Aspect'
    description = Column(db.Text, label='Описание')

    parent_id = db.Column(db.Integer, db.ForeignKey('SubCriterion.id'))
    sub_criterion = db.relationship('SubCriterion', backref=db.backref('Aspect', lazy='dynamic'))

    calculation_id = Column(db.Integer,
                            db.ForeignKey('Calculation.id'),
                            label='Метод',
                            # TODO info={'choices': [(c.id, c.name) for c in db.session.query(Calculation).all()]}
                            )
    calculation = db.relationship('Calculation', backref=db.backref('Aspect', lazy='dynamic'))

    def __str__(self):
        return '<Критерий: "%s" (%s)>' % (self.name, self.max_balls)


# Участник, связь всех оценок за аспекты и олимпиады
class Member(db.Model):
    __tablename__ = 'Member'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(db.Text, nullable=False, default="Участник")

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
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

    member_id = db.Column(db.Integer, db.ForeignKey('Member.id'))
    member = db.relationship('Member', backref=db.backref('MemberAssessment', lazy='dynamic'))
    ball = Column(db.Integer, nullable=False)

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
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    assessment = Column(db.Float, label='Оценка', nullable=False)

    user_id = Column(db.Integer, db.ForeignKey('User.id'))
    user = db.relationship('User', backref=db.backref('ExpertAssessment', lazy='dynamic'))

    member_assessment_id = Column(db.Integer, db.ForeignKey('MemberAssessment.id'))
    member_assessment = db.relationship('MemberAssessment', backref=db.backref('ExpertAssessment', lazy='dynamic'))
