#!/usr/bin/env python

"""Tests for `pi_logger` package."""

# import pytest
import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pi_logger.local_loggers import (getserial, read_config,
                                     save_readings_to_db, add_local_pi_info)
from pi_logger.local_db import (set_up_database, get_last_reading,
                                get_recent_readings)

BASE = declarative_base()
TEST_DB_PATH = os.getcwd()
TEST_DB_FILENAME = "test.db"
TEST_DB_FILEPATH = os.path.join(TEST_DB_PATH, TEST_DB_FILENAME)
CONN_STRING = f'sqlite:///{TEST_DB_FILEPATH}'
ENGINE = create_engine(CONN_STRING, echo=False)

TEST_TIME = datetime.now()


def test_serial():
    """
    Check getserial returns a string
    """
    assert isinstance(getserial(), str)


def test_read_config():
    """
    Check that read_config returns dataframes for both sensor types
    """
    piname = "catflap"
    config_path = ""
    config_file = "logger_config.csv"
    sensor_dict = read_config(piname, config_path, config_file)
    assert isinstance(sensor_dict["bme680"], pd.DataFrame)
    assert isinstance(sensor_dict["dht22"], pd.DataFrame)


def test_create_db():
    """Test creating the SQLite DB"""
    set_up_database(TEST_DB_PATH, ENGINE)
    assert os.path.exists(TEST_DB_FILEPATH)


def test_save_readings():
    """
    Check that readings saved into the db actually end up there
    """
    reading_time = datetime.now()
    test_type = "test_reading"
    test_val = -999.999
    data = dict(
        datetime=reading_time,
        sensortype=test_type,
        temp=test_val,
        humidity=test_val,
        pressure=test_val,
    )
    pi_id = "7357"
    pi_name = "testy"
    location = "testsville"
    data = add_local_pi_info(data, pi_id, pi_name, location)
    save_readings_to_db(data, ENGINE)

    last_reading = get_last_reading(engine=ENGINE)
    assert isinstance(last_reading, dict)
    assert last_reading['datetime'] == reading_time
    assert last_reading['sensortype'] == test_type
    assert last_reading['temp'] == test_val
    assert last_reading['piid'] == pi_id
    assert last_reading['location'] == location


def test_recent_readings():
    """
    Check that readings saved into the db actually end up there
    """
    reading_time = datetime.now()
    test_type = "test_reading"
    test_val = -999.999
    data = dict(
        datetime=reading_time,
        sensortype=test_type,
        temp=test_val,
        humidity=test_val,
        pressure=test_val,
    )
    pi_id = "7357"
    pi_name = "testy"
    location = "testsville"
    data = add_local_pi_info(data, pi_id, pi_name, location)
    save_readings_to_db(data, ENGINE)

    recent_readings = get_recent_readings(start_datetime=TEST_TIME,
                                          engine=ENGINE)
    assert recent_readings is not None
    recent_readings = pd.DataFrame(recent_readings)
    recent_readings['datetime'] = pd.to_datetime(recent_readings['datetime'],
                                                 format="%Y-%m-%d %H:%M:%S")
    assert reading_time in recent_readings['datetime'].to_list()
