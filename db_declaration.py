
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class ImageInfo(Base):
    __tablename__ = 'Image'

    id = Column(Integer, primary_key=True)
    path = Column(String(), nullable=False)
    name = Column(String(), nullable=False)
    format = Column(String(), nullable=True)
    lat = Column(Float())
    lon = Column(Float())
    dateTime = Column(DateTime)

class Person(Base):
    __tablename__ = 'Person'

    id = Column(Integer, primary_key=True)
    prename = Column(String(), nullable=False)
    lastname = Column(String(), nullable=False)

class Faces(Base):
    __tablename__ = 'Faces'
    id = Column(Integer, primary_key=True)
    imageId = Column(Integer, ForeignKey(Person.id))
    path = Column(String(), nullable=False)
    person = Column(Integer, ForeignKey(Person.id))

class PersonOnImage(Base):
    __tablename__ = 'PersonOnImage'
    id = Column(Integer, primary_key=True)
    personId = Column(Integer, ForeignKey(Person.id))
    imageId = Column(Integer, ForeignKey(ImageInfo.id))

engine = create_engine('sqlite:///photos.db', echo=True)

Base.metadata.create_all(engine)

