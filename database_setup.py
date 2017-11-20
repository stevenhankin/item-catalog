"""Create database schema for project."""
from sqlalchemy import Column, ForeignKey, Integer, String, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from database_populate import populate
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class User(Base):
    """Application user for a (logged-in) session.
    The Amazon User ID is unique for the user + application """

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250))
    client_id = Column(String(250))

    def to_json(self):
        return {"user": {"id": self.id, "name": self.name, "email": self.email, "picture": self.picture,
                         "amazon_id": self.client_id}}


class Category(Base):
    """Category groups together related items."""

    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def to_json(self):
        return {"category": {"id": self.id, "name": self.name, "user_id": self.user_id}}


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
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def to_json(self):
        return {"item": {"id": self.id, "name": self.name, "category_id": self.category_id, "user_id": self.user_id,
                         "description": self.description, "timeCreated": self.time_created,
                         "timeUpdated": self.time_updated}}


engine = create_engine('postgresql://catalog:catalog2017@localhost:5432/itemcatalogdb')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

Base.metadata.create_all(engine)

# ONLY when the database setup module is called directly
# the intention will be to populate the database too
if __name__ == "__main__":
    populate(session, User, Category, Item)
