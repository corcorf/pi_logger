from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from local_db import LocalData
import os


def get_last_local_record():
    log_path = os.path.join(os.path.expanduser("~"), "logs")
    db_path = os.path.join(log_path, "locallogs.db")
    conn_string = 'sqlite:///{}'.format(db_path)
    engine = create_engine(conn_string, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(LocalData).slice(-2, -1).first()
    return result


if __name__ == "__main__":
    result = get_last_local_record()
    print(result)
