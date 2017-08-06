from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    #address = Column(String(250))
    #city = Column(String(80))
    #state = Column(String(20))
    #zipCode = Column(String(10))
    #website = Column(String)
    
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    #gender = Column(String(6), nullable = False)
    #dateOfBirth = Column(Date)
    #picture = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    #weight = Column(Numeric(10))


engine = create_engine('sqlite:///itemcategories.db')
 

Base.metadata.create_all(engine)
