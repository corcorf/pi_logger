"""
adapted from:
https://www.codementor.io/@sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq
"""

from flask import Flask
from flask_restful import Resource, Api
from local_db import LocalData, ENGINE
import pandas as pd
from sqlalchemy.orm import sessionmaker
# from print_last_local_record import get_last_local_record
# from datetime import datetime, timedelta

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
        js = df.to_json()
        return js


class GetLast(Resource):
    def get(self):
        session = Session()
        table = LocalData
        q = session.query(table)\
                   .order_by(table.datetime.desc())
        result = q.first()
        df = pd.DataFrame(result.get_row(), index=[0])
        df['datetime'] = pd.to_datetime(df['datetime'],
                                        format="%Y-%m-%d %H:%M:%S")
        js = df.to_json()
        return js

# class LocalHumidityLocation(Resource):
#     def get(self, location):
#         with db_connect.connect() as conn:
#             q = "select datetime, location, humidity from localdata where location like {location};"
#             query = conn.execute(q)
#             result = {'data': [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
#         return jsonify(result)


api.add_resource(GetRecent, '/get_recent/<start_datetime>')
api.add_resource(GetLast, '/get_last')
# api.add_resource(LocalHumidityLocation, '/humidity/<location>')  # Route_3


if __name__ == '__main__':
    app.run(port='5002', debug=True)
