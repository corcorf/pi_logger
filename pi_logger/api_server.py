"""
adapted from:
https://www.codementor.io/@sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq
"""

import pandas as pd
from flask import Flask
from flask_restful import Resource, Api
from sqlalchemy.orm import sessionmaker
from local_db import LocalData, ENGINE
from local_loggers import PINAME, LOG_PATH
from local_loggers import set_up_python_logging, getserial, initialise_sensors
from local_loggers import poll_once

app = Flask(__name__)
api = Api(app)

Session = sessionmaker(bind=ENGINE)


class GetRecent(Resource):
    def get(self, start_datetime):
        session = Session()
        table = LocalData
        start_datetime = pd.to_datetime(start_datetime)
        q = session.query(table)\
                   .filter(table.datetime > start_datetime)
        i = q.values("datetime", "location", "sensortype", "piname", "piid",
                     "temp", "humidity", "pressure", "gasvoc")
        df = pd.DataFrame(i)
        df['datetime'] = pd.to_datetime(df['datetime'],
                                        format="%Y-%m-%d %H:%M:%S")
        return df.to_json()


class GetLast(Resource):
    def get(self):
        session = Session()
        table = LocalData
        q = session.query(table).order_by(table.datetime.desc())
        result = q.first()
        df = pd.DataFrame(result.get_row(), index=[0])
        if df.size:
            df['datetime'] = pd.to_datetime(df['datetime'],
                                            format="%Y-%m-%d %H:%M:%S")
        return df.to_json()


class PollSensors(Resource):
    def get(self):
        set_up_python_logging(pi_name=PINAME, debug=False)
        piid = getserial()
        engine = ENGINE
        dht_sensor, dht_config, bme_sensor, bme_config = \
            initialise_sensors(pi_name=PINAME,
                               config_path=LOG_PATH,
                               config_fn='logger_config.csv')
        # msg = 'Performing one-off logging of sensors connected to {pi_name}'
        # LOG.info(msg)
        poll_once(dht_config, dht_sensor, bme_config, bme_sensor, piid,
                  pi_name=PINAME, engine=engine)


api.add_resource(GetRecent, '/get_recent/<start_datetime>')
api.add_resource(GetLast, '/get_last')
api.add_resource(PollSensors, '/poll_sensors')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002', debug=True)
