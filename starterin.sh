#!/bin/bash 
forever start -a -l /home/$USER/erin/logs/erin.log -e err.log -c python3 --sourceDir /home/$USER/erin/src/ main.py
sleep 1
echo "DONE"
