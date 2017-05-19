import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'users.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
