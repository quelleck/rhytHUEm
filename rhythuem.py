#! /usr/bin/env python3
# RhytHUEm
# Ethan Seyl 2016

import configparser
import logging
import logging.config
import do

config = configparser.ConfigParser()
config.read('/home/pi/rhytHUEm/config/rhythuem.ini')
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
    logging.config.fileConfig('/home/pi/rhytHUEm/config/logging.conf')
    main()
