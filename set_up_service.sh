#! /bin/bash

# check to see if this has been done already
if [ ! -e logger_service_set_up_complete ]
then
  service_name=logger
  unit_file=$service_name.service
  timer_file=$service_name.timer
  service_path=/etc/systemd/system/
  # set up logging as a service
  echo "creating $unit_file in $service_path"
  cat > $service_path$unit_file << EOF
[Unit]
Description=Take readings from sensors listed in $HOME/logs/logger_config.csv

[Service]
WorkingDirectory=$PWD
User=$USER
ExecStart=$PWD/env/bin/python3 pi_logger/local_loggers.py --debug

[Install]
WantedBy=multi-user.target
EOF
  echo "Creating $timer_file in $service_path"
  cat > $service_path$timer_file << EOF
[Unit]
Description=Schedule reading of sensors listed in $HOME/logs/logger_config.csv

[Timer]
OnCalendar=*-*-* *:00/5:00
Unit=$unit_file

[Install]
WantedBy=multi-user.target
EOF
  echo "reloading systemd daemon and enabling service"
  systemctl daemon-reload
  systemctl start logger.service
  systemctl enable logger.service
  echo "creating file 'logger_service_set_up_complete as flag"
  touch logger_service_set_up_complete
fi
