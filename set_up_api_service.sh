#! /bin/bash

# check to see if this has been done already
if [ ! -e api_service_set_up_complete ]
then
  service_name=api_server
  unit_file=$service_name.service
  service_path=/etc/systemd/system/
  # set up logging as a service
  echo "creating $unit_file in $service_path"
  cat > $service_path$unit_file << EOF
[Unit]
Description=Run flask api server for logger data
echo "After=multi-user.target"

[Service]
WorkingDirectory=$PWD
User=$USER
ExecStart=$PWD/env/bin/python3 pi_logger/api_server.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF
  echo "reloading systemd daemon and enabling service"
  systemctl daemon-reload
  systemctl start api_server.service
  systemctl enable api_server.service
  echo "creating file 'api_service_set_up_complete as flag"
  touch api_service_set_up_complete
fi
