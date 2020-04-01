#!/usr/bin/env python

"""
Tests for `pi_logger.local_loggers` module.
Separated from db tests because sensor dependencies are uninstallable
on Travis CI"""

# import pytest
import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pi_logger.local_loggers import (getserial, read_config)

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
