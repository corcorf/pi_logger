#!/usr/bin/env python

"""
Tests for `pi_logger.sql_tables`module.
Separated from sensor tests and api tests because sensor dependencies are
uninstallable on Travis CI
"""

# import pytest
import os
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from pi_logger.local_db import (set_up_database, save_readings_to_db,
                                get_last_reading, get_recent_readings)

BASE = declarative_base()
TEST_DB_PATH = os.getcwd()
TEST_TIME = datetime.now().strftime("%Y%m%d%H%M%S")
TEST_DB_FILENAME = f"test_{TEST_TIME}.db"
TEST_DB_FILEPATH = os.path.join(TEST_DB_PATH, TEST_DB_FILENAME)
CONN_STRING = f'sqlite:///{TEST_DB_FILEPATH}'
ENGINE = create_engine(CONN_STRING, echo=False)

TEST_TIME = datetime.now()

TEST_DATA = dict(
    datetime=datetime.now(),
    location="testsville",
    sensortype="test_reading",
    piname="testy",
    piid="7357",
    temp=-999.999,
    humidity=-999.999,
    pressure=-999.999,
    gasvoc=-999.999,
    mcdvalue=-999.999,
    mcdvoltage=-999.999,
)


def test_create_db():
    """Test creating the SQLite DB"""
    set_up_database(TEST_DB_PATH, ENGINE)
    assert os.path.exists(TEST_DB_FILEPATH)


def test_save_readings():
    """
    Check that readings saved into the db actually end up there
    """
    save_readings_to_db(TEST_DATA, ENGINE)
    last_reading = get_last_reading(engine=ENGINE)
    assert last_reading == TEST_DATA


def test_recent_readings():
    """
    Check that readings saved into the db actually end up there
    """
    save_readings_to_db(TEST_DATA, ENGINE)

    recent_readings = get_recent_readings(start_datetime_utc=TEST_TIME,
                                          engine=ENGINE)
    recent_readings = pd.DataFrame(recent_readings)
    recent_readings['datetime'] = pd.to_datetime(recent_readings['datetime'],
                                                 format="%Y-%m-%d %H:%M:%S")
    assert TEST_DATA['datetime'] in recent_readings['datetime'].to_list()
