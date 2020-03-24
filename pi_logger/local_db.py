import os
import logging
from sqlalchemy import create_engine, distinct, CheckConstraint
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float, BigInteger
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import psycopg2

BASE = declarative_base()
LOG_PATH = os.path.join(os.path.expanduser("~"), "logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
DB_PATH = os.path.join(LOG_PATH, "locallogs.db")
CONN_STRING = 'sqlite:///{}'.format(DB_PATH)
ENGINE = create_engine(CONN_STRING, echo=False)
# Session = sessionmaker(bind=ENGINE)


class LocalData(BASE):
    """
    Class for sensor data table in local SQLite DB
    _______
    columns:
        id (Integer)
        datetime (DateTime)
        location (String)
        sensortype (String)
        piname (string)
        piid (string)
        temp (Float)
        humidity (Float)
        pressure (Float)
        gasvoc (Float)
    """
    __tablename__ = 'localdata'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    location = Column(String)
    sensortype = Column(String)
    piname = Column(String)
    piid = Column(String)
    temp = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    gasvoc = Column(Float)

    sqlite_autoincrement = True

    def __repr__(self):
        info = (self.piname, self.location, self.datetime)
        return "<LocalData(pi={}, sensor={}, datetime={})>".format(*info)

    def get_row(self):
        data = dict(
            datetime=self.datetime,
            location=self.location,
            sensortype=self.sensortype,
            piname=self.piname,
            piid=self.piid,
            temp=self.temp,
            humidity=self.humidity,
            pressure=self.pressure,
            gasvoc=self.gasvoc,
        )
        return data


# class LocalSensors(BASE):
#     """
#     Class for sensors table in local SQLite DB
#     _______
#     columns:
#         piname (String)
#         piid (String)
#         sensorname (String)
#         pin (Integer)
#     """
#     __tablename__ = 'localsensors'
#     piname = Column(String)
#     piid = Column(String)
#     sensorname = Column(String)
#     pin = Column(Integer)
#
#     def __repr__(self):
#         info = (self.piname, self.location, self.pin)
#         return "<LocalSensor(pi={}, sensor={}, pin={})>".format(*info)


def set_up_database(path, engine):
    """
    Set up or connect to an SQLite database
    Return the database connection
    """
    if not os.path.exists(path):
        os.mkdir(path)
    BASE.metadata.create_all(engine)


def one_or_more_results(query):
    """
    Return True if query contains one or more results, otherwise False
    """
    try:
        q.one()
    except NoResultFound:
        return False
    except MultipleResultsFound:
        pass
    return True


if __name__ == "__main__":
    set_up_database(LOG_PATH, ENGINE)
