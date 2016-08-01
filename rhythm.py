#! /usr/bin/env python3
# Rhythm
# Ethan Seyl 2016

import config
import do


#do.initial_wait()
run_program = True
do.check_for_bluetooth()
device_away = True
while run_program:
    user_detected = do.check_for_device(config.device_mac.split())
    if user_detected and device_away:
        ct_settings = do.arrived_home()
        device_away = False

    elif user_detected and device_away is False:
        do.home(ct_settings)

    elif user_detected is False and device_away is False:
        do.left()
        device_away = True

    elif user_detected is False and device_away:
        do.gone()
