import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Flask
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "users.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Mail
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USERNAME = "no.reply.grades.csqc@gmail.com"
MAIL_PASSWORD = os.getenv("PASSWORD")
MAIL_USE_TLS = False
MAIL_USE_SSL = True
