import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    DATABASE_CONNECT_OPTIONS = {}
    THREADS_PER_PAGE = 2
    # CSRF_ENABLED     = True
    # CSRF_SESSION_KEY = os.urandom(23)

    SECRET_KEY = os.urandom(23)

class DevelopConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
