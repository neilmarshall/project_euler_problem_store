"""
Production configuration for Flask Application
"""
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config():
    """ Production configuration for Flask Application """
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True,
                                 'pool_recycle': 3600,
                                 'echo_pool': True,
                                 'pool_size': 4}
    SOLUTIONS_TO_SHOW = 12
    SQLALCHEMY_ECHO = True
    PROPAGATE_EXCEPTIONS = True
