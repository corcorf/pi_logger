"""
Load existing data stored in a csv file to the sqlite database
"""

import os
import socket
import pandas as pd
from sqlalchemy import create_engine
from local_db import LocalData
from local_loggers import getserial


def load_existing_data_to_db(existing_log=None,
                             db_path=None):
    """
    Load existing data stored in a csv file to the sqlite database
    """
    pi_name = socket.gethostname()
    if existing_log is None:
        existing_log = os.path.join(os.path.expanduser("~"), "logs",
                                    f"log_{pi_name}.csv")

    if db_path is None:
        log_path = os.path.join(os.path.expanduser("~"), "logs")
        if not os.path.exists(log_path):
            os.mkdir(log_path)
            db_path = os.path.join(log_path, "locallogs.db")

    data = pd.read_csv(existing_log)
    data = data.rename(columns={k: k.lower() for k in data.columns})
    data = data.rename(columns={"relhum": "humidity", "airquality": "gasvoc",
                                "name": "location", "pi": "piname"})
    data["datetime"] = pd.to_datetime(data["datetime"],
                                      format="%d/%m/%Y %H:%M:%S")
    data['piid'] = getserial()
    conn_string = 'sqlite:///{}'.format(db_path)
    engine = create_engine(conn_string, echo=True)
    data.to_sql(LocalData.__tablename__, engine, if_exists="append",
                index=False)


if __name__ == "__main__":
    load_existing_data_to_db()