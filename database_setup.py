import os
import sys
from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    items = relationship("CatalogItem", cascade="all, delete-orphan")


class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    catalogitems = relationship("CatalogItem", cascade="all, delete-orphan")

    @property
    def serialize(self):
        return {
                'Name': self.name,
                'Id': self.id,
                'items':
                [catalogitems.serialize for catalogitems in self.catalogitems]
                }


class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(500))
    datecreated = Column(DateTime(), default=datetime.utcnow)
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
                'name': self.name,
                'description': self.description,
                'id': self.id,
                'Category': self.catalog.name,
                }


engine = create_engine('sqlite:///catalogmenu.db')


Base.metadata.create_all(engine)
