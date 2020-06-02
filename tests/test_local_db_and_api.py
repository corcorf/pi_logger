#!/usr/bin/env python

"""
Tests for `pi_logger.sql_tables` and `pi_logger.api_server` modules.
Separated from sensor tests because sensor dependencies are uninstallable
on Travis CI
"""

# import pytest
import os
from datetime import datetime

import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from pi_logger.local_db import (set_up_database, save_readings_to_db,
                                get_last_reading, get_recent_readings)
from pi_logger.api_server import GetRecent, GetLast, check_api_result

BASE = declarative_base()
TEST_DB_PATH = os.getcwd()
TEST_DB_FILENAME = "test.db"
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


def test_check_api_result():
    """
    Test that an api result without datetime field fails check function
    """
    result_without_datetime = ""
    pytest.raises(AssertionError, check_api_result, result_without_datetime)


def test_get_recent():
    """
    Check get_recent returns a json with necessary fields
    """
    start_datetime = datetime(1970, 1, 1, 0, 0)
    route = GetRecent()
    route_result = route.get(start_datetime, engine=ENGINE)
    assert check_api_result(route_result)


def test_get_last():
    """
    Check get_last returns a json with necessary fields
    """
    route = GetLast()
    route_result = route.get(engine=ENGINE)
    assert check_api_result(route_result)
