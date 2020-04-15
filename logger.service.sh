echo "# created from logger.service.sh"
echo "[Unit]"
echo "Description=Log relative humidity and temperature"
echo "After=multi-user.target"
echo
echo "[Service]"
echo "WorkingDirectory=$PWD"
echo "User=$USER"
echo "ExecStart=$PWD/env/bin/python3 pi_logger/local_loggers.py --freq 300 --debug"
echo
echo "[Install]"
echo "WantedBy=multi-user.target"
