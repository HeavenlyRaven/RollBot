#!/bin/bash
# creating /heroes directory
mkdir heroes
# creating config.json
echo '{"token": "", "admin_id": null, "group_id": null}' > config.json
# creating queues.json
echo '{}' > queues.json
echo "Bot setup finished successfully. Please, configure it via config.json file."