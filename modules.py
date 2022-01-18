from dataclasses import dataclass
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime

database_filename = 'database.db'
project_dir = os.path.dirname(os.path.abspath(__file__))
database = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db=SQLAlchemy()
def create_db(app, database=database):
    app.config['SQLALCHEMY_DATABASE_URI']=database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db.app=app
    db.init_app(app)
    db.create_all()

class inheritedClassName(db.Model):
    __abstract__ = True

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return self.__dict__

@dataclass
class Items(inheritedClassName):
    id: int
    name: String
    count: int
    in_time: DateTime
    in_price: Integer

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    count = Column(Integer, default=0)
    in_time = Column(DateTime)
    in_price = Column(Integer)

@dataclass
class Sales(inheritedClassName):
    id: int
    name: String
    count: int
    in_time: DateTime
    in_price: Integer
    out_time: DateTime
    out_price: Integer

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    count = Column(Integer, default=0)
    in_time = Column(DateTime)
    in_price = Column(Integer)
    out_time = Column(DateTime)
    out_price = Column(Integer)

@dataclass
class Imports(inheritedClassName):
    id: int
    name: String
    count: int
    in_time: DateTime
    in_price: Integer

    __tablename__ = "imports"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    count = Column(Integer, default=0)
    in_time = Column(DateTime)
    in_price = Column(Integer)