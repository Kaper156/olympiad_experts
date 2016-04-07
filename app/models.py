from app import db
from flask_sqlalchemy import event
from sqlalchemy_defaults import make_lazy_configured, Column

make_lazy_configured(db.mapper)

# Списки методов
subjective_methods = [
    # ('Шкала 10', 'lambda x: 1')
    ('Оценка от 0-10 (коэффициент)', 'lambda x: x/10')
]
objective_methods = [
    ('Наличие', 'lambda x: bool(x)'),
    ('Коэффициент', 'lambda x: x/10'),  # Оценка в диапозоне 0-10
    # ('Диапозон-5', 'lambda x: x//5'),
    # ('Диапозон-10', 'lambda x: x//10'),
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
    password = Column(db.String, label='Пароль', nullable=False, info={'trim': False})

    roles = db.relationship('Role', back_populates='user')


class Role(db.Model):
    __tablename__ = 'Role'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    user = db.relationship('User', back_populates='roles')

    privilege_id = db.Column(db.Integer, db.ForeignKey('Privilege.id'))
    privilege = db.relationship('Privilege', backref=db.backref('Role', lazy='dynamic'))

    olympiad_id = db.Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad_experts = db.relationship("Olympiad", back_populates="experts")
    olympiad_chief_experts = db.relationship("Olympiad", back_populates="chief_expert")


def load_users():
    if db.session.query(User).count() == 0:
        query = db.session.query(Privilege)
        privilege_admin = query.filter(Privilege.rights == R_ADMIN).first()
        privilege_expert = query.filter(Privilege.rights == R_EXPERT).first()
        users = [('Expert1', privilege_admin),
                 ('Expert2', privilege_admin),
                 ('Expert3', privilege_admin),
                 ('Expert4', privilege_admin),
                 ('Expert5', privilege_admin),
                 ('Admin', privilege_admin)]
        from os import urandom
        for login, privilege in users:
            user = User()
            user.login = login
            user.password = 'qwerty12345'
            user.privilege_id = privilege.id
            db.session.add(user)
        db.session.commit()


def reload_users():
    from os import urandom
    query = db.session.query(User).all()
    for user in query:
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
    
    def get_olympiad(self):
        # Иерархичный список элементов олимпиады
        classes = [Olympiad, Criterion, SubCriterion, Aspect]

        # Ограничение списка до текущего
        classes = classes[:classes.index(self.__class__)]
        obj = self
        while classes:
            next_cls = classes.pop()
            obj = db.session.query(next_cls).get(obj.parent_id)
        return obj


# Мероприятие
class Olympiad(db.Model):
    __tablename__ = 'Olympiad'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(db.String, label='Название', nullable=False)
    date = Column(db.Date, label='Дата (ГГГГ.ММ.ДД)', nullable=False)
    description = Column(db.String, label='Описание')

    # TODO
    # один (в будущем- роль)
    chief_expert = db.relationship('Role',
                                   uselist=True,
                                   back_populates="olympiad_chief_experts",
                                   cascade="all, delete-orphan")
    # обычно 5
    experts = db.relationship('Role',
                              back_populates="olympiad_experts",
                              cascade="all, delete-orphan")
    member_count = Column(db.Integer, label='Количество участников', default=2)
    members = db.relationship('Member',
                              back_populates="olympiad",
                              cascade="all, delete-orphan")
    status = Column(db.Integer, label='Статус', default=0)

    children = db.relationship('Criterion', cascade="all, delete-orphan")

    def __str__(self):
        return '<Олимпиада: "%s" от [%s]>' % (self.name, self.date)

    def start(self):
        # todo можно выставлять оценки
        print('Начата %s ' % self.__str__())
        self.status = 1

    def close(self):
        # todo подсчет результатов доступен
        print('Завершена %s ' % self.__str__())
        self.status = 2


@event.listens_for(Olympiad, 'after_insert')
def after_insert_olympiad(mapper, connection, olympiad):
    # Todo можно изменять шаблон а создаются участники (от количества)
    # Участники олимпиады
    for index in range(1, olympiad.member_count+1):
        
        member = Member()
        member.olympiad_id = olympiad.id
        member.olympiad = olympiad
        member.order_number = index
        db.session.add(member)
    # эскпертная группа
    # for index in range(5):
    #     role = Role()
    #     role.olympiad_id = olympiad.id
    #     role.olympiad_experts = olympiad
    #     olympiad.experts.append(role)

    # Старший эксперт
    admin_privilege = db.session.query(Privilege).filter(Privilege.rights == R_ADMIN).first()
    admin = db.session.query(User).filter(User.login == 'Admin').first()
    role = Role()
    role.olympiad_id = olympiad.id
    role.olympiad_chief_experts = olympiad
    # TODO
    role.privilege = admin_privilege
    role.privilege_id = admin_privilege.id

    role.user = admin
    role.user_id = admin.id
    # TODO

    olympiad.chief_expert = [role]
    olympiad.status = 0


# Часть олимпиады: Настройка сетевого оборудования, etc
class Criterion(OlympiadBase):
    __tablename__ = 'Criterion'
    parent_id = Column(db.Integer, db.ForeignKey('Olympiad.id'))
    children = db.relationship("SubCriterion", cascade="all, delete-orphan")

    def __str__(self):
        return '<Модуль: "%s" (%s)>' % (self.name, self.max_balls)


# Часть привязанная к конкретной области: ОС Linux, Программирование на Python
class SubCriterion(OlympiadBase):
    __tablename__ = 'SubCriterion'
    parent_id = Column(db.Integer, db.ForeignKey('Criterion.id'))
    children = db.relationship('Aspect', cascade="all, delete-orphan")

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
    #     for calc in db.session.query(Calculation).all():
    #         db.session.delete(calc)
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
    description = Column(db.Text, label='Описание', nullable=True)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('SubCriterion.id'))

    calculation_id = Column(db.Integer,
                            db.ForeignKey('Calculation.id'),
                            label='Метод',
                            # TODO info={'choices': [(c.id, c.name) for c in db.session.query(Calculation).all()]}
                            # TODO with try construction
                            )
    calculation = db.relationship('Calculation',
                                  backref=db.backref('Aspect', lazy='dynamic'))

    member_assessments = db.relationship('MemberAssessment', cascade="all, delete-orphan")#, back_populates='aspect_id')

    def __str__(self):
        return '<Критерий: "%s" (%s)>' % (self.name, self.max_balls)


@event.listens_for(Aspect, 'after_insert')
def after_insert_aspect(mapper, connection, aspect):
    olympiad = aspect.get_olympiad()
    for member in olympiad.members:
        member_assessment = MemberAssessment()
        member_assessment.aspect_id = aspect.id
        member_assessment.member_id = member.id
        member.assessments.append(member_assessment)
        aspect.member_assessments.append(member_assessment)


# Участник, связь всех оценок за аспекты и олимпиады
class Member(db.Model):
    __tablename__ = 'Member'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    order_number = Column(db.Integer, label='Номер', nullable=False)
    FIO = Column(db.Text, label="ФИО", nullable=False, default="Инкогнито")

    olympiad_id = db.Column(db.Integer, db.ForeignKey('Olympiad.id'))
    olympiad = db.relationship("Olympiad", back_populates="members")

    assessments = db.relationship('MemberAssessment',
                                  uselist=True,
                                  back_populates="member",
                                  cascade="all, delete-orphan")

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
    member = db.relationship('Member', back_populates="assessments")
    ball = Column(db.Integer, nullable=False, default=0)

    aspect_id = db.Column(db.Integer, db.ForeignKey('Aspect.id'))
    aspect = db.relationship("Aspect", back_populates="member_assessments")

    expert_assessments = db.relationship('ExpertAssessment',
                                         uselist=True,
                                         back_populates="member_assessment",
                                         cascade="all, delete-orphan")

    def calc(self):
        result = []
        for assessment in self.expert_assessments:
            result.append(assessment.assessment)
        aspect = db.session.query(Aspect).get(self.aspect_id)
        self.ball = aspect.calculation.calc(result, aspect.max_balls)
        return self.ball


# Оценка эксперта за аспект
class ExpertAssessment(db.Model):
    __tablename__ = 'ExpertAssessment'
    id = Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    assessment = Column(db.Float, label='Оценка', default=0)

    user_id = Column(db.Integer, db.ForeignKey('User.id'))
    user = db.relationship('User', backref=db.backref('ExpertAssessment', lazy='dynamic'))

    member_assessment_id = Column(db.Integer, db.ForeignKey('MemberAssessment.id'))
    member_assessment = db.relationship('MemberAssessment', back_populates="expert_assessments")


@event.listens_for(MemberAssessment, 'after_insert')
def after_insert_member_assessment(mapper, connection, member_assessment):
    member = db.session.query(Member).get(member_assessment.member_id)
    experts = member.olympiad.experts
    chief = member.olympiad.chief_expert
    # TODO DANGER
    for expert in chief:
        expert_assessment = ExpertAssessment()

        # expert_assessment.member_assessment_id = member_assessment.id
        # expert_assessment.member_assessment = member_assessment

        expert_assessment.user_id = expert.id
        # expert_assessment.user = expert
        expert_assessment.member_assessment_id = member_assessment.id
        member_assessment.expert_assessments.append(expert_assessment)

