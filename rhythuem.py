#! /usr/bin/env python3
# RhytHUEm
# Ethan Seyl 2016

import configparser
import logging
import logging.config
import do
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read('{}/config/rhythuem.ini'.format(dir_path))
device_list = (config['DEFAULT']['DeviceMac']).split()

def main():
    do.blink_ready()
    device_away = True
    while True:
        user_detected = do.check_for_device(device_list)
        if user_detected and device_away:
            light_settings = do.arrived_home()
            device_away = False

        elif user_detected and device_away is False:
            do.home(light_settings)

        elif user_detected is False and device_away is False:
            do.left()
            device_away = True

        elif user_detected is False and device_away:
            do.gone()


if __name__ == "__main__":
    logging.config.fileConfig('{}/config/logging.conf'.format(dir_path))
    main()
