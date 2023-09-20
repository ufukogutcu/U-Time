from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    SECRET_KEY = environ.get('SECRET_KEY')

    BCRYPT_LOG_ROUNDS = 4

    SQLALCHEMY_DATABASE_URI =  'sqlite:///' + path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = 'amqp://ufiyo:2007@localhost:5672/'
    #CELERY_RESULT_BACKEND = ''
