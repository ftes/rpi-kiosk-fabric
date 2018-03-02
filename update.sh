#!/bin/sh

cd %(code_dir)s
git pull
npm install
sudo systemctl restart %(service_name)s

# refresh browser
sleep 1m
export DISPLAY=:0.0 && xdotool key ctrl+r
