#!/bin/bash
cd /home/sharmanator/adhdtaskmanager
python3 app.py &
sleep 2
chromium --kiosk --noerrdialogs --disable-infobars http://localhost:5001
