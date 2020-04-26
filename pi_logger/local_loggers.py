"""
Log ambient atmospheric conditions at a specified frequency
"""

import os
import time
import logging
from datetime import datetime

import pandas as pd
import Adafruit_DHT
import bme680
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

from pi_logger import PINAME, LOG_PATH
from pi_logger.local_db import ENGINE, save_readings_to_db
from pi_logger.cli import get_local_logger_arguments


LOG = logging.getLogger(f"pi_logger_{PINAME}.local_loggers")


def getserial():
    """
    Extract serial from cpuinfo file and return as string
    https://www.raspberrypi-spy.co.uk/2012/09/getting-your-raspberry-pi-serial-number-using-python/
    Returns string corresponding to:
        cpu serial number where "Serial" is found in /proc/cpuinfo
        "0000000000000000" where /proc/cpuinfo missing line beginning "Serial"
        "ERROR000000000" where /proc/cpuinfo does not exist
    """
    LOG.info("attempting to get cpu serial number")
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as file:
            for line in file:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
    except FileNotFoundError:
        cpuserial = "ERROR000000000"
    return cpuserial


def read_config(pi_name, path=LOG_PATH, filename='logger_config.csv'):
    """
    Read local config file from path to determine which loggers should be set
    up
    Return dictionary of logger_type: list_of_loggers
    """
    LOG.info("reading local logger config")
    file_path = os.path.join(path, filename)
    config = pd.read_csv(file_path, index_col=1)
    config = config[config['name'] == pi_name]
    dht_sensors = config[config['type'] == 'dht22']
    bme_sensors = config[config['type'] == 'bme680']
    sensors = {"dht22": dht_sensors, "bme680": bme_sensors}

    messages = [
        'dht22_loggers: {}'.format(', '.join(dht_sensors.index.tolist())),
        'bme680_loggers: {}'.format(', '.join(bme_sensors.index.tolist())),
    ]
    for msg in messages:
        LOG.info(msg)

    return sensors


def set_up_dht22_sensors():
    """
    Return an instance of the DHT22 sensor class
    """
    LOG.info("setting up dht22 sensor")
    return Adafruit_DHT.DHT22


def set_up_bme680_sensors():
    """
    Return an instance of the BME680 sensor class
    """
    LOG.info("setting up bme680 sensor")
    try:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)
    return sensor


def set_up_mcp_convertor():
    """
    Return an instance of the MCP analog-to-digital converter for reading
    the soil moisture probe
    """
    spi_bus = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    chip_select = digitalio.DigitalInOut(board.D5)
    return MCP.MCP3008(spi_bus, chip_select)


def poll_dht22(sensor, pin):
    """
    Get a reading from a DHT22 sensor and return data as a dictionary
    """
    time_now = datetime.now()
    LOG.info('%s polling DHT22 sensor on pin %s',
             time_now.strftime("%Y-%m-%d %H:%M:%S"), pin)
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is None and temperature is None:
        LOG.info('%s failed to retrieve data from DHT22 sensor at pin %s',
                 time_now.strftime("%Y-%m-%d %H:%M:%S"), pin)
        data = None
    else:
        data = dict(
            datetime=time_now,
            sensortype="dht22",
            temp=temperature,
            humidity=humidity,
        )
    return data


def poll_bme680(sensor, pin):
    """
    Get a reading from a BME680 sensor and return data as a dictionary
    """
    time_now = datetime.now()
    LOG.info('%s polling BME680 sensor on pin %s',
             time_now.strftime("%Y-%m-%d %H:%M:%S"), pin)
    if sensor.get_sensor_data():
        data = dict(
            datetime=time_now,
            sensortype="bme680",
            temp=sensor.data.temperature,
            humidity=sensor.data.humidity,
            pressure=sensor.data.pressure,
        )
        if sensor.data.heat_stable:
            data['gasvoc'] = sensor.data.gas_resistance
    else:
        LOG.info('%s failed to retrieve data from BME680 sensor at pin %s',
                 time_now.strftime("%Y-%m-%d %H:%M:%S"), pin)
        data = None
    return data


def poll_mcp3008(mcp_chip, pin):
    """
    Get a reading from a sensor connected to an MCP analog-to-digital converter
    and return data as a dictionary
    """
    time_now = datetime.now()
    LOG.info('%s polling MCP chip on pin %s',
             time_now.strftime("%Y-%m-%d %H:%M:%S"), pin)
    chan = AnalogIn(mcp_chip, getattr(MCP, f"P{pin}"))
    adc_val = chan.value
    adc_volt = chan.voltage
    if adc_val is None and adc_volt is None:
        LOG.info('%s failed to retrieve data from sensor at MCP pin %s',
                 time_now.strftime("%Y-%m-%d %H:%M:%S"), pin)
        data = None
    else:
        data = dict(
            datetime=time_now,
            sensortype="MCP",
            mcdvalue=adc_val,
            mcdvoltage=adc_volt,
        )
    return data


def add_local_pi_info(data, pi_id, pi_name, location):
    """
    Take a dictionary of data read from a sensor and add information relating
    to the pi from which the data was being collected
    Returns a dictionary with the extra information
    """
    if data is not None:
        data['location'] = location
        data['piname'] = pi_name
        data['piid'] = pi_id
    return data


def poll_all_dht22(dht_config, dht_sensor, pi_id, pi_name, engine):
    """
    Poll all dht22 sensors listed in the config file for this pi
    Save resulting records to the database specified engine
    """
    if dht_sensor is not None:
        for location, details in dht_config.iterrows():
            dht_pin = int(details.pin)
            data = poll_dht22(dht_sensor, dht_pin)
            data = add_local_pi_info(data, pi_id, pi_name, location)
            save_readings_to_db(data, engine)


def poll_all_bme680(bme_config, bme_sensor, pi_id, pi_name, engine):
    """
    Poll all bme680 sensors listed in the config file for this pi
    Save resulting records to the database specified engine
    """
    if bme_sensor is not None:
        for location, details in bme_config.iterrows():
            bme_pin = int(details.pin)
            data = poll_bme680(bme_sensor, bme_pin)
            data = add_local_pi_info(data, pi_id, pi_name, location)
            save_readings_to_db(data, engine)


def poll_all_mcp3008(mcp_config, mcp_chip, pi_id, pi_name, engine):
    """
    Poll all sensors connected to MCP3008 listed in the config file for this pi
    Save resulting records to the database specified engine
    """
    if mcp_chip is not None:
        for location, details in mcp_config.iterrows():
            mcp_pin = int(details.pin)
            data = poll_mcp3008(mcp_chip, mcp_pin)
            data = add_local_pi_info(data, pi_id, pi_name, location)
            save_readings_to_db(data, engine)


def initialise_sensors(pi_name=PINAME,
                       config_path=LOG_PATH,
                       config_fn='logger_config.csv'):
    """
    Initialise the DHT22 and BME680 sensors
    Return the sensor instances and dataframes containing the config parameters
    """
    sensors = read_config(
        pi_name=pi_name, path=config_path, filename=config_fn
    )

    dht_config = sensors["dht22"]
    if dht_config.size:
        dht_sensor = set_up_dht22_sensors()
    else:
        dht_sensor = None

    bme_config = sensors["bme680"]
    if bme_config.size:
        bme_sensor = set_up_bme680_sensors()
    else:
        bme_sensor = None

    mcp_config = sensors["mcp3008"]
    if mcp_config.size:
        mcp_chip = set_up_mcp_convertor()
    else:
        mcp_chip = None
    return dht_sensor, dht_config, bme_sensor, bme_config, mcp_chip, mcp_config


if __name__ == "__main__":
    PIID = getserial()
    ARGS = get_local_logger_arguments()
    FREQ = ARGS.frequency
    DEBUG = ARGS.debug

    DHT_SENSOR, DHT_CONF, BME_SENSOR, BME_CONF, MCP_CHIP, MCP_CONF = \
        initialise_sensors(pi_name=PINAME,
                           config_path=LOG_PATH,
                           config_fn='logger_config.csv')

    if FREQ is None:
        LOG.info('Performing one-off logging of sensors connected to %s',
                 PINAME)
        poll_all_dht22(DHT_CONF, DHT_SENSOR, PIID, PINAME, ENGINE)
        poll_all_bme680(BME_CONF, BME_SENSOR, PIID, PINAME, ENGINE)
        poll_all_mcp3008(MCP_CONF, MCP_CHIP, PIID, PINAME, ENGINE)
    else:
        LOG.info('Will log sensors connected to %s at frequency of %s s',
                 PINAME, FREQ)
        while True:
            poll_all_dht22(DHT_CONF, DHT_SENSOR, PIID, PINAME, ENGINE)
            poll_all_bme680(BME_CONF, BME_SENSOR, PIID, PINAME, ENGINE)
            poll_all_mcp3008(MCP_CONF, MCP_CHIP, PIID, PINAME, ENGINE)
            time.sleep(FREQ)
