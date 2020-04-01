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
from sqlalchemy.orm import sessionmaker
from local_db import LocalData, ENGINE, one_or_more_results
from local_loggers import PINAME, LOG_PATH
from local_loggers import set_up_python_logging, getserial, initialise_sensors
from local_loggers import poll_all_dht22, poll_all_bme680

app = Flask(__name__)
api = Api(app)

Session = sessionmaker(bind=ENGINE)


class GetRecent(Resource):
    """
    API resource to provide all readings since a given start_datetime
    """
    # pylint: disable=R0201
    def get(self, start_datetime):
        """
        GetRecent API resource get function
        """
        session = Session()
        table = LocalData
        start_datetime = pd.to_datetime(start_datetime)
        query = session.query(table)\
                       .filter(table.datetime > start_datetime)
        if one_or_more_results(query):
            result = query.values(
                "datetime", "location", "sensortype", "piname",
                "piid", "temp", "humidity", "pressure", "gasvoc"
            )
            result = pd.DataFrame(result)
            result['datetime'] = pd.to_datetime(result['datetime'],
                                                format="%Y-%m-%d %H:%M:%S")
            result = result.to_json()
        else:
            msg = '{"message": "query returns no results"}'
            result = json.loads(msg)
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
        session = Session()
        table = LocalData
        query = session.query(table).order_by(table.datetime.desc())
        if one_or_more_results(query):
            result = query.first()
            result = pd.DataFrame(result.get_row(), index=[0])
            if result.size:
                result['datetime'] = pd.to_datetime(result['datetime'],
                                                    format="%Y-%m-%d %H:%M:%S")
            result = result.to_json()
        else:
            msg = '{"message": "query returns no results"}'
            result = json.loads(msg)
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
