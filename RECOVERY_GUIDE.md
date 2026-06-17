# SHARMANATOR DISASTER RECOVERY GUIDE

## 1. Environment Restore
Navigate to the app folder and run:
pip install -r requirements.txt

## 2. Remote Drive Restore
Run the handshake again to link the new OS to Google Drive:
rclone config
- Choose 'n' (New), name it 'googledrive', type '24' (Google Drive).
- Leave IDs blank, choose scope '1', 'y' for auto-auth.

## 3. Automation Restore
Re-enable the hourly backup:
crontab -e
- Scroll to the bottom and paste:
0 * * * * /home/sharmanator/adhd-task-app/backup_db.sh

## 4. Kiosk Restore
Re-enable the auto-start dashboard:
nano /home/sharmanator/.config/lxsession/LXDE-pi/autostart
- Add this to the bottom:
@bash /home/sharmanator/adhd-task-app/launch_board.sh
