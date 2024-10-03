from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
