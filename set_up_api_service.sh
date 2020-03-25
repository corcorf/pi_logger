#! /bin/bash

# check to see if this has been done already
if [ ! -e api_service_set_up_complete ]
then
  # set up api server as a service
  echo "copying api_server.service to  /etc/systemd/system/"
  cp api_server.service /etc/systemd/system/
  echo "reloading systemd daemon and enabling service"
  systemctl daemon-reload
  systemctl start api_server.service
  systemctl enable api_server.service
  echo "creating file 'api_service_set_up_complete as flag"
  touch api_service_set_up_complete
fi
