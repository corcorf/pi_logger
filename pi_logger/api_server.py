"""
API for the pi_logger module

adapted from:
https://www.codementor.io/@sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq
"""
# pylint: disable=C0103

import json
import logging
import urllib

import pandas as pd
from flask import Flask, render_template, url_for
from flask_restful import Resource, Api
from pi_logger import PINAME, LOG_PATH
from pi_logger.local_db import (ENGINE, get_recent_readings,
                                get_last_reading)
from pi_logger.local_loggers import getserial, initialise_sensors
from pi_logger.local_loggers import (poll_all_dht22, poll_all_bme680,
                                     poll_all_mcp3008)

app = Flask(__name__)
api = Api(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

LOG = logging.getLogger(f"pi_logger_{PINAME}.api_server")


class GetRecent(Resource):
    """
    API resource to provide all readings since a given start_datetime (UTC)
    """
    # pylint: disable=R0201
    def get(self, start_datetime_utc, engine=ENGINE):
        """
        GetRecent API resource get function
        """
        start_datetime_utc = pd.to_datetime(start_datetime_utc)
        result = get_recent_readings(start_datetime_utc, engine=engine)
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
    def get(self, engine=ENGINE):
        """
        GetLast API resource get function
        """
        result = get_last_reading(engine=engine)
        if result is None:
            msg = '{"message": "query returns no results"}'
            result = json.loads(msg)
        else:
            result = pd.DataFrame(result, index=[0])
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
        piid = getserial()
        engine = ENGINE
        dht_sensor, dht_conf, bme_sensor, bme_conf, mcp_chip, mcp_conf = \
            initialise_sensors(pi_name=PINAME,
                               config_path=LOG_PATH,
                               config_fn='logger_config.csv')
        # msg = 'Performing one-off logging of sensors connected to {pi_name}'
        # LOG.info(msg)
        poll_all_dht22(dht_conf, dht_sensor, piid, PINAME, engine)
        poll_all_bme680(bme_conf, bme_sensor, piid, PINAME, engine)
        poll_all_mcp3008(mcp_conf, mcp_chip, piid, PINAME, engine)


def check_api_result(result):
    """
    Check that the result of an API request contains a datetime and temperature
    or else is an error message
    Used for automated testing
    """
    assert isinstance(result, str)
    converted_result = json.loads(result)
    assert isinstance(converted_result, dict)
    keys = converted_result.keys()
    assert "datetime" in keys or "message" in keys
    assert "temp" in keys or "message" in keys
    return True


@app.route('/')
def main_page():
    """
    Render the main page with a table of available API routes
    """
    table = pd.DataFrame()
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        url = urllib.parse.unquote(url)
        table.loc[rule.endpoint, "Methods"] = methods
        table.loc[rule.endpoint, "URL"] = url
    table.index = table.index.rename("Endpoint")
    table = table.reset_index()
    context = dict(
        title=f"Pi Logger: {PINAME}",
        subtitle="Available routes:",
        table=table.to_html(justify='left', table_id="routes", index=False),
    )
    return render_template('site_map.html', **context)


api.add_resource(GetRecent, '/get_recent/<start_datetime_utc>')
api.add_resource(GetLast, '/get_last')
api.add_resource(PollSensors, '/poll_sensors')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5003', debug=False)
