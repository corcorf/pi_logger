#! /bin/bash

# check to see if this has been done already
if [ ! -e local_db_set_up_complete ]
then
  # create database and import existing records
  echo "running local_db.py"
  python3 pi_logger/local_db.py
  echo "running import_existing.py"
  python3 pi_logger/import_existing.py

  # set up logging as a service
  echo "copying logger.service to  /etc/systemd/system/"
  cp logger.service /etc/systemd/system/logger.service
  echo "reloading systemd daemon and enabling service"
  systemctl daemon-reload
  systemctl start logger.service
  systemctl enable logger.service

  echo "creating file 'local_db_set_up_complete' as flag"
  touch local_db_set_up_complete
fi
