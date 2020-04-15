echo "# created from api_server.services.sh"
echo "[Unit]"
echo "Description=Run flask api server for logger data"
echo "After=multi-user.target"
echo
echo "[Service]"
echo "WorkingDirectory=$PWD"
echo "User=$USER"
echo "ExecStart=$PWD/env/bin/python3 pi_logger/api_server.py"
echo
echo "[Install]"
echo "WantedBy=multi-user.target"
