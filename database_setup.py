from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Categories(Base):
    __tablename__ = 'categories'
   
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
       	   'id'           	: self.id,
       	   'title'         	: self.title,
           'namdescription' : self.description,   
       }

class CategorieItem(Base):
    __tablename__ = 'categorie_item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    categorie_id = Column(Integer, ForeignKey('categories.id'))
    categorie = relationship(Categories)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        	'id': self.id,
            'title': self.title,
            'description': self.description,
        }

engine = create_engine('sqlite:///catalogitem.db')


Base.metadata.create_all(engine)