#!/bin/bash
pgrep -f rhythuem.py
if [ $? -eq 0 ]; then
    echo "Process is running."
else
    echo "Process is not running...starting."
    sudo systemctl start rhythuem.service
fi