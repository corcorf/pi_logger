import os
import logging
from sqlalchemy import create_engine, distinct, CheckConstraint
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float, BigInteger
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.inspection import inspect
import psycopg2

BASE = declarative_base()
LOG_PATH = os.path.join("home", "pi", "logs")
DB_PATH = os.path.join(LOG_PATH, "locallogs.db")
CONN_STRING = 'sqlite:///{}'.format(DB_PATH)
ENGINE = create_engine(CONN_STRING, echo=False)
SESSION = sessionmaker(bind=ENGINE)


class LocalData(BASE):
    """
    Class for sensor data table in local SQLite DB
    _______
    columns:
        datetime (DateTime)
        location (String)
        piname (string)
        piid (string)
        pin (Integer)
        temp (Float)
        humidity (Float)
        pressure (Float)
        gasvoc (Float)
    """
    __tablename__ = 'localdata'

    datetime = Column(DateTime, primary_key=True)
    location = Column(String)
    piname = Column(String)
    piid = Column(String, primary_key=True)
    pin = Column(Integer, primary_key=True)
    temp = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    gasvoc = Column(Float)

    def __repr__(self):
        info = (self.piname, self.location, self.datetime)
        return "<LocalData(pi={}, sensor={}, datetime={})>".format(*info)


class LocalSensors(BASE):
    """
    Class for sensors table in local SQLite DB
    _______
    columns:
        piname (String)
        piid (String)
        sensorname (String)
        pin (Integer)
    """
    __tablename__ = 'localsensors'
    piname = Column(String)
    piid = Column(String)
    sensorname = Column(String)
    pin = Column(Integer)

    def __repr__(self):
        info = (self.piname, self.location, self.pin)
        return "<LocalSensor(pi={}, sensor={}, pin={})>".format(*info)


def set_up_database(path, engine):
    """
    Set up or connect to an SQLite database
    Return the database connection
    """
    if not os.path.exists(path):
        os.mkdir(path)
    BASE.metadata.create_all(engine)


if __name__ == "__main__":
    set_up_database(LOG_PATH, CONN_STRING)
