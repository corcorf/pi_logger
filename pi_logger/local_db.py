"""
Defines SQL tables for the local SQLite database on a raspberry pi
as well as functions for frequently used queries. Tables are defined
and handled using the SQLalchemy ORM.
"""

import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect

from pi_logger import PINAME, LOG_PATH

BASE = declarative_base()
DB_PATH = os.path.join(LOG_PATH, "locallogs.db")
CONN_STRING = 'sqlite:///{}'.format(DB_PATH)
ENGINE = create_engine(CONN_STRING, echo=False)

LOG = logging.getLogger(f"pi_logger_{PINAME}.local_db")


class LocalData(BASE):
    """
    Class for sensor data table in local SQLite DB
    _______
    columns:
        id (Integer)
        datetime (DateTime) # utc
        location (String)
        sensortype (String)
        piname (string)
        piid (string)
        temp (Float)
        humidity (Float)
        pressure (Float)
        gasvoc (Float)
        mcdvalue (Integer)
        mcdvoltage (Float)
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
    mcdvalue = Column(Integer)
    mcdvoltage = Column(Float)

    sqlite_autoincrement = True

    def __repr__(self):
        info = (self.piname, self.location, self.datetime)
        return "<LocalData(pi={}, sensor={}, datetime={})>".format(*info)

    def get_row(self):
        """
        Return a dictionary containing the readings for a paricular time and
        sensor, complete with the full sensor information.
        """
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
            mcdvalue=self.mcdvalue,
            mcdvoltage=self.mcdvoltage,
        )
        return data


def set_up_database(path, engine):
    """
    Set up or connect to an SQLite database
    Return the database connection
    """
    if not os.path.exists(path):
        LOG.info("Creating dir: %s", path)
        os.mkdir(path)
    LOG.info("Attempting to create db")
    BASE.metadata.create_all(engine)


def save_readings_to_db(data, engine):
    """
    Save data from one of the sensors to the local database
    """
    if data is not None:
        LOG.debug("attempting to write data to db")
        data = LocalData(**data)
        session = sessionmaker(bind=engine)()
        session.add(data)
        session.flush()
        session.commit()
    else:
        LOG.debug("skipping writing of data. data is None")


def one_or_more_results(query):
    """
    Return True if query contains one or more results, otherwise False
    """
    try:
        query.one()
    except NoResultFound:
        return False
    except MultipleResultsFound:
        pass
    return True


def get_recent_readings(start_datetime_utc, table=LocalData, engine=ENGINE):
    """
    Get all readings since startdate from the local DB
    returns an iterator containing the results or None
    """
    session = sessionmaker(bind=engine)()
    LOG.debug("Querying db for data since %s", start_datetime_utc)
    query = session.query(table)\
                   .filter(table.datetime > start_datetime_utc)
    if one_or_more_results(query):
        output_cols = [c.name for c in inspect(table).columns]
        result = query.values(*output_cols)
    else:
        LOG.debug("No results from query")
        result = None
    return result


def get_last_reading(table=LocalData, engine=ENGINE):
    """
    Get most recent reading from the local DB
    returns a dictionary containing the results or None
    """
    session = sessionmaker(bind=engine)()
    LOG.debug("Querying for last reading")
    query = session.query(table).order_by(table.datetime.desc())
    if one_or_more_results(query):
        result = query.first().get_row()
    else:
        LOG.debug("No results from query (last)")
        result = None
    return result


if __name__ == "__main__":
    set_up_database(LOG_PATH, ENGINE)
