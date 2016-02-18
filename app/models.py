from app import db
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship


# Конкретное задание: Установить ОС Windows Xp
class Aspect(db.Model):
    __tablename__ = 'Aspect'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    description = Column(Text)
    measurements = relationship("Measurements")

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

# Хранит конкретные методы вычисления
class MeasurementType(db.Model):
    __tablename__ = 'MeasurementType'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    description = Column(String)
    # TODO хранить текст лямбда функций?
    method = Column(Text)
    measurements = relationship("Measurements")

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
