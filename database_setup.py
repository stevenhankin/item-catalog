"""Create database schema for project."""
from sqlalchemy import Column, ForeignKey, Integer, String, func
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """Application user for a (logged-in) session."""

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250))


class Category(Base):
    """Category groups together related items."""

    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Item(Base):
    """Items represent things grouped by categories."""

    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    description = Column(String(4000), nullable=False)
    time_created = Column(DATETIME(fsp=6), server_default=func.now())
    time_updated = Column(DATETIME(timezone=True, fsp=6), onupdate=func.now())


engine = create_engine('sqlite:///itemcategories.db')


Base.metadata.create_all(engine)


