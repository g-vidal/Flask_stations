from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_caching import Cache
# from sqlalchemy.ext.declarative import DECLARATIVE_BASE
# from sqlalchemy.ext.mypy.names import DECLARATIVE_BASE

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
