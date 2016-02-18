from app import db
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship


class Element(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    max_balls = Column(Float, nullable=False)

    def __init__(self, name, max_balls):
        self.name = name
        self.max_balls = max_balls

    def __repr__(self):
        return """
<row class="element element-{3} {0}">
    <column cols="9" class="info">
        <p class="name">Название:<span>{1}</span></p>
        <p class="balls">Максимум баллов:<span>{2}</span></p>
        <div class="editor editor-{3} {0}"></div>
    </column>
    <column cols="3" class="buttons">
        <h3>
            <a href="#" class="add"     ><span class="icon_plus_alt2"></span> </a>
            <a href="#" class="delete"  ><span class="icon_close_alt2"></span> </a>
            <a href="#" class="edit"    ><span class="icon_pencil-edit"></span> </a>
            <a href="#" class="child"   ><span class="icon_menu-circle_alt2"></span> </a>
        </h3>
    </column>
</row>
""".format(self.__class__.__name__,
           self.name,
           self.max_balls,
           self.id)


class Olympiad(Element):
    __tablename__ = 'Olympiad'
    description = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    children = relationship("Section")

    def __init__(self, name, max_balls, description, date=None, children=list()):
        Element.__init__(self,
                         name=name,
                         max_balls=max_balls)
        self.description = description
        self.date = date
        self.children = children


class Section(Element):
    __tablename__ = 'Section'
    children = relationship("Task")
    parent_id = Column(Integer, ForeignKey('Olympiad.id'))

    def __init__(self, name, max_balls, children=list(), parent_id=None):
        Element.__init__(self,
                         name=name,
                         max_balls=max_balls)
        self.children = children
        self.parent_id = parent_id


class Task(Element):
    __tablename__ = 'Task'
    children = relationship("SubTask")
    parent_id = Column(Integer, ForeignKey('Section.id'))

    def __init__(self, name, max_balls, children=list(), parent_id=None):
        Element.__init__(self,
                         name=name,
                         max_balls=max_balls)
        self.children = children
        self.parent_id = parent_id


class SubTask(Element):
    __tablename__ = 'SubTask'
    children = relationship("Criterion")
    parent_id = Column(Integer, ForeignKey('Task.id'))

    def __init__(self, name, max_balls, children=list(), parent_id=None):
        Element.__init__(self,
                         name=name,
                         max_balls=max_balls)
        self.children = children
        self.parent_id = parent_id


class Criterion(Element):
    __tablename__ = 'Criterion'
    parent_id = Column(Integer, ForeignKey('SubTask.id'))

    def __init__(self, name, max_balls, parent_id=None):
        Element.__init__(self,
                         name=name,
                         max_balls=max_balls)
        self.parent_id = parent_id