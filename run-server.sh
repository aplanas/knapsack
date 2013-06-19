#! /bin/bash

echo "Please, be sure that ssh-agent is running and have your identity."
echo "You can do (ssh-agent && ssh-add)."

python run-when.py --lock lock-dir/kp.lock --run ./full-kp.sh
