#!/bin/sh
# Runs from /etc/rc.local
# sync_db needs to run from crontab
runuser -l pi -c 'cd /home/pi/HHSAccessControlV4; screen -dmS doorman python /home/pi/HHSAccessControlV4/tag_reader.py'
