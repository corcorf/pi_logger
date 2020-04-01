#!/usr/bin/env python

"""
Tests for `pi_logger.api_server` module.
Separated from db tests because sensor dependencies are uninstallable
on Travis CI
"""

# import pytest
import json
from datetime import datetime
from pi_logger.api_server import GetRecent, GetLast


def check_result(result):
    """
    Check that the result of an API request contains a datetime and temperature
    or else is an error message
    """
    assert isinstance(result, str)
    converted_result = json.loads(result)
    assert isinstance(converted_result, dict)
    keys = converted_result.keys()
    assert "datetime" in keys or "message" in keys
    assert "temp" in keys or "message" in keys


def test_get_recent():
    """
    Check get_recent returns a json with necessary fields
    """
    start_datetime = datetime(1970, 1, 1, 0, 0)
    route = GetRecent()
    route_result = route.get(start_datetime)
    check_result(route_result)


def test_get_last():
    """
    Check get_last returns a json with necessary fields
    """
    route = GetLast()
    route_result = route.get()
    check_result(route_result)
