#! /usr/bin/env python3
# Rhythm
# Ethan Seyl 2016

import config
import logging
import logging.config
import do


def main():
    do.check_for_bluetooth()
    device_away = True
    while True:
        user_detected = do.check_for_device(config.device_mac.split())
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
    logging.config.fileConfig("/home/pi/rhythm/config/logging.conf")
    main()
