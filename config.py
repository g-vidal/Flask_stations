import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # APPLICATION_ROOT = '/mining'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'orientation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #DEBUG = True,
    #CACHE_TYPE = "memcachedCache",
    #CACHE_DEFAULT_TIMEOUT = 7200 # il faut certainement vérifier que le cache n'est pas vide et le recharger au besoin