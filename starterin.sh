#!/bin/bash 

# this script is only for my vps to automatically trigger the bot via a github workflow
# you do not need this file, instead run the following in your terminal
#
# pipenv install --ignore-pipfile
# pipenv python src/main.py

forever start -a -l /home/$USER/erin/logs/erin.log -e err.log -c "pipenv run python3" --workingDir /home/$USER/erin/src/ --sourceDir /home/$USER/erin/src/ main.py 
echo "DONE"
