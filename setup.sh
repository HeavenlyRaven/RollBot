#!/bin/bash
# creating /heroes directory
mkdir heroes
# creating config.json
echo '{"token": "", "admin_id": null, "group_id": null}' > config.json
# creating queues.json
echo '{}' > queues.json
# creating a virtual environment
python3 -m venv ./rollbot_env
# installing dependencies
./rollbot_env/bin/python3 -m pip install -r requirements.txt
echo "Bot setup finished successfully. Please, configure it via config.json file."