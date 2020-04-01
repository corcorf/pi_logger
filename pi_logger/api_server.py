"""
API for the pi_logger module

adapted from:
https://www.codementor.io/@sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq
"""
# pylint: disable=C0103

import json
import pandas as pd
from flask import Flask
from flask_restful import Resource, Api
from local_db import ENGINE, get_recent_readings, get_last_reading
from local_loggers import PINAME, LOG_PATH
from local_loggers import set_up_python_logging, getserial, initialise_sensors
from local_loggers import poll_all_dht22, poll_all_bme680

app = Flask(__name__)
api = Api(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


class GetRecent(Resource):
    """
    API resource to provide all readings since a given start_datetime
    """
    # pylint: disable=R0201
    def get(self, start_datetime):
        """
        GetRecent API resource get function
        """
        start_datetime = pd.to_datetime(start_datetime)
        result = get_recent_readings(start_datetime)
        if result is None:
            msg = '{"message": "query returns no results"}'
            result = json.loads(msg)
        else:
            result = pd.DataFrame(result)
            result['datetime'] = pd.to_datetime(result['datetime'],
                                                format="%Y-%m-%d %H:%M:%S")
            result = result.to_json()
        return result


class GetLast(Resource):
    """
    API resource to provide the last recorded set of readings
    """
    # pylint: disable=R0201
    def get(self):
        """
        GetLast API resource get function
        """
        result = get_last_reading()
        if result is None:
            msg = '{"message": "query returns no results"}'
            result = json.loads(msg)
        else:
            result = pd.DataFrame(result, index=[0])
            result['datetime'] = pd.to_datetime(result['datetime'],
                                                format="%Y-%m-%d %H:%M:%S")
            result = result.to_json()
        return result


class PollSensors(Resource):
    """
    API resource to trigger a sensor polling event
    """
    # pylint: disable=R0201
    def get(self):
        """
        PollSensors API resource get function
        """
        set_up_python_logging(debug=False)
        piid = getserial()
        engine = ENGINE
        dht_sensor, dht_config, bme_sensor, bme_config = \
            initialise_sensors(pi_name=PINAME,
                               config_path=LOG_PATH,
                               config_fn='logger_config.csv')
        # msg = 'Performing one-off logging of sensors connected to {pi_name}'
        # LOG.info(msg)
        poll_all_dht22(dht_config, dht_sensor, piid, PINAME, engine)
        poll_all_bme680(bme_config, bme_sensor, piid, PINAME, engine)


api.add_resource(GetRecent, '/get_recent/<start_datetime>')
api.add_resource(GetLast, '/get_last')
api.add_resource(PollSensors, '/poll_sensors')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002', debug=False)
