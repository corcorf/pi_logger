#! /bin/bash

# check to see if this has been done already
if [ ! -e local_db_set_up_complete ]
then
  # create database and import existing records
  echo "running local_db.py"
  python3 pi_logger/local_db.py
  echo "running import_existing.py"
  python3 pi_logger/import_existing.py

  echo "creating file 'local_db_set_up_complete' as flag"
  touch local_db_set_up_complete

  echo "moving logger_config.csv to ~/logs/"
  cp logger_config.csv ~/logs/
fi
