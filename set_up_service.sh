#! /bin/bash

# check to see if this has been done already
if [ ! -e logger_service_set_up_complete ]
then
  # set up logging as a service
  echo "copying logger.service to  /etc/systemd/system/"
  cp logger.service /etc/systemd/system/logger.service
  echo "reloading systemd daemon and enabling service"
  systemctl daemon-reload
  systemctl start logger.service
  systemctl enable logger.service
  echo "creating file 'logger_service_set_up_complete as flag"
  touch logger_service_set_up_complete
fi
