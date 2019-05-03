import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456789'
    SQLALCHEMY_DATABASE_URI = r'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOLUTIONS_TO_SHOW = 12
