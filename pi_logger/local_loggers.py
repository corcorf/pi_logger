#! /usr/bin/python3
"""
Log ambient atmospheric conditions at a specified frequency
"""

import time
from datetime import datetime
import Adafruit_DHT
import bme680
import argparse
import pandas as pd
import socket
import logging
from sqlalchemy.orm import sessionmaker

from local_db import LocalData, ENGINE


def getserial():
    """
    Extract serial from cpuinfo file and return as string
    https://www.raspberrypi-spy.co.uk/2012/09/getting-your-raspberry-pi-serial-number-using-python/
    Returns string corresponding to:
        cpu serial number where "Serial" is found in /proc/cpuinfo
        "0000000000000000" where /proc/cpuinfo missing line beginning "Serial"
        "ERROR000000000" where /proc/cpuinfo does not exist
    """
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except FileNotFoundError:
        cpuserial = "ERROR000000000"
    return cpuserial


def read_config(pi_name, path='../logger_config.csv'):
    """
    Read local config file from path to determine which loggers should be set
    up
    Return dictionary of logger_type: list_of_loggers
    """
    config = pd.read_csv(path, index_col=0)
    config = config[config['pi'] == pi_name]
    dht_sensors = config[config['type'] == 'dht22']
    bme_sensors = config[config['type'] == 'bme680']
    sensors = {"dht22": dht_sensors, "bme680": bme_sensors}

    messages = [
        'dht22_loggers: {}'.format(', '.join(dht_sensors.index.tolist())),
        'bme680_loggers: {}'.format(', '.join(bme_sensors.index.tolist())),
    ]
    for m in messages:
        logging.info(m)

    return sensors


def set_up_dht22_sensors():
    """
    Return an instance of the DHT22 sensor class
    """
    return Adafruit_DHT.DHT22


def set_up_bme680_sensors():
    """
    Return an instance of the BME680 sensor class
    """
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


def pause_to_make_times_nice(frequency):
    """
    Sleep before taking the first reading so that the reading times line up
    nicely with the hour
    """
    if frequency >= 60 and frequency % 60 == 0:
        print('waiting to start readings')
        while time.localtime().tm_min % (frequency // 60) != 0:
            print(time.localtime().tm_min)


def poll_dht22(sensor, pin):
    """
    Get a reading from a DHT22 sensor and return data as a dictionary
    """
    time = datetime.now()
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f'{time_string} polling DHT22 sensor on pin {pin}')
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        data = dict(
                datetime=time,
                pin=pin,
                temp=temperature,
                humidity=humidity,
            )
        return data
    else:
        message = '{} failed to retrieve data from DHT22 sensor at pin {}'
        logging.info(message.format(time_string, pin))


def poll_bme680(sensor, pin):
    """
    Get a reading from a BME680 sensor and return data as a dictionary
    """
    time = datetime.now()
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f'{time_string} polling BME680 sensor on pin {pin}')
    if sensor.get_sensor_data():
        if sensor.data.heat_stable:
            airquality = sensor.data.gas_resistance
        else:
            airquality = None
        data = dict(
            datetime=time,
            pin=pin,
            temp=sensor.data.temperature,
            humidity=sensor.data.humidity,
            pressure=sensor.data.pressure,
            airquality=airquality
        )
        return data
    else:
        message = '{} failed to retrieve data from BME680 sensor at pin {}'
        logging.info(message.format(time_string, pin))


def save_readings_to_db(data, engine):
    """
    Save data from one of the sensors to the local database
    """
    if data is not None:
        logging.debug("attempting to write data to db")
        data = LocalData(**data)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(data)
        session.flush()
        session.commit()
    else:
        logging.debug("skipping writing of data. data is None")


def get_arguments(default_freq=300):
    """
    Get a reading frequency as an argument when the script is run from CLI
    """
    logging.debug("fetching arguments")
    description = 'Log ambient conditions at a specified frequency.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('frequency', metavar='freq', type=int,
                        default=default_freq,
                        help='Frequency of readings in seconds')
    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='set the logging module to debug mode')
    return parser.parse_args()


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


if __name__ == "__main__":
    args = get_arguments(default_freq=300)
    freq = args.frequency
    debug = args.debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(filename='debug.log', level=logging.INFO)
    piid = getserial()
    piname = socket.gethostname()
    engine = ENGINE

    msg = 'Will log sensors connected to {pi_name} at frequency of {freq}s'
    logging.info(msg)

    sensors = read_config(pi_name=piname,
                          path='../logger_config.csv')
    dht_list = sensors["dht22"]
    bme_list = sensors["bme680"]
    dht_sensor = set_up_dht22_sensors()
    bme680_sensor = set_up_bme680_sensors()

    while True:
        new_data = list()
        for location, details in dht_list.iterrows():
            dht_pin = int(details.pin1)
            data = poll_dht22(dht_sensor, dht_pin)
            data = add_local_pi_info(data, piid, piname, location)
            save_readings_to_db(data, engine)

        for location, details in bme_list.iterrows():
            bme_pin = int(details.pin1)
            data = poll_bme680(bme680_sensor, bme_pin)
            data = add_local_pi_info(data, piid, piname, location)
            save_readings_to_db(data, engine)

        time.sleep(freq)
