#!/usr/bin/env python

"""
Tests for `pi_logger.local_loggers` module.
Separated from db tests because sensor dependencies are uninstallable
on Travis CI"""

# import pytest
import pandas as pd
from pi_logger.local_loggers import (getserial, read_config)


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
    assert (
        isinstance(sensor_dict["bme680"], pd.DataFrame)
        and isinstance(sensor_dict["dht22"], pd.DataFrame)
    )
