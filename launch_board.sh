#!/bin/bash
# 1. Kill existing versions to free up Port 5000
pkill -f app.py

# 2. Navigate and launch the Flask app backend
cd /home/sharmanator/adhd-task-app
/usr/bin/python3 app.py &

# 3. Wait for the Brain to wake up
sleep 10

# 4. Launch Chromium in Kiosk mode - Cleaned of OS login flags
chromium --kiosk --noerrdialogs --disable-infobars --disable-restore-session-state http://127.0.0.1:5000
