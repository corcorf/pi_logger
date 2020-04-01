"""
Test script. Retrieves last record on local sqlite db and prints result
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pi_logger.local_db import LocalData


def get_last_local_record():
    """
    Return last record on local sqlite db
    """
    log_path = os.path.join(os.path.expanduser("~"), "logs")
    db_path = os.path.join(log_path, "locallogs.db")
    conn_string = 'sqlite:///{}'.format(db_path)
    engine = create_engine(conn_string, echo=True)
    session = sessionmaker(bind=engine)()
    result = session.query(LocalData).slice(-2, -1).first()
    return result


if __name__ == "__main__":
    LAST_RECORD = get_last_local_record()
    print(LAST_RECORD)
