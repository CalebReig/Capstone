"""
This file contains all configurations/environment variables for the application.
Namely -- testing config, development config (default), production config
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    The Config class is the parent class to the application configurations.
    This class contains all environment variables for the application.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ahe$%fAfRR3'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'reigadatest@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJ_PREFIX = '[Patient Health Monitoring]'
    MAIL_SENDER = 'PHM'
    ADMIN = os.environ.get('ADMIN') or 'reigadacaleb@gmail.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    The DevelopmentConfig class is the application configuration during development
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """
    The TestingConfig class is the application configuration during testing
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    """
    The ProductionConfig class is the application configuration during production
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = { #dict of configurations refenced when app is initialized
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}