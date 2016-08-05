# rhytHUEm

rhytHUEm is a customizable bluetooth proximity and color temperature (think f.lux) controller for Philips Hue lights built specifically for a Raspberry Pi. 

REQS
-Python 3
-Pysolar (installed with pip3)
-Bluetooth
-Internet connection

#Features
- Bluetooth proximity detection to turn lights on/off. Use any bluetooth device, no pairing required (for most devices).
- Changes the color temperature of your lights throughout the day based on your location and the altitude of the Sun over the horizon. Smart enough to not override your settings if you make a change with another app. #HealthyCircadianRhythms
- Unlimited number of devices can be used for proximity detection.


#HOW IT WORKS
RhytHUEm sends a bluetooth pair request to your device(s) every 20 seconds when you're away. When your device is in range, no matter if the pair is successful, it will register you as "home". It then uses pysolar to determine the altitude of the sun in the sky based on the long/lat set in the config.py file and the time of day. It will send a PUT request to the light group you set in config.py with an updated color temperature. When you're registered as home, every three minutes it will 1) make sure your device is still in range 2) check to see if you've made any manual changes to the ct or bri values of your lights, and if not 3) update the color temperature of your lights. If you do make a manual change, RhytHUEm will stop making CT changes until you leave/come back. It does this every three minutes until you leave or bluetooth is turned off on your device. Once you're "away" RhytHUEm will turn off your lights and start sending pair requests every 20 seconds until you return.

Key Items: RhytHUEm only scans for your device every 3 minutes after it turns your lights on. If you leave, it could take up to 2 minutes 59 seconds to turn your lights off. Give it time before you troubleshoot. Same for when you arrive - it could take up to 20 seconds once you've gotten in range. You can change these values easily in do.py.

#Installing
- Make sure you have your pi set to the correct time or else the color temperature of your lights will be off.
- Clone the repo to your home directory 

git clone https://github.com/quelleck/rhytHUEm/
- Copy rhythuem.service to /lib/systemd/system/

sudo cp ~/rhytHUEm/rhythuem.service /lib/systemd/system/

-Make sure rhythuem.service has the correct permissions

sudo chmod 644 /lib/systemd/system/rhythuem.service
- Run this command to get the script to start when you boot the pi 

sudo systemctl daemon-reload
sudo systemctl enable rhythuem.service
- Open config/logging.py file 

nano ~/rhytHUEm/config.py

-Add your Hue API key, device MAC address, longitude, latitude, and light group. Consult the Philips Hue developer pages to find this info if needed.


- Install pysolar for tracking the sun


sudo pip3 install pysolar


You can use 

sudo systemctl status rhythuem.service

to check on the status, start, and stop the service.



TROUBLESHOOTING: If the app turns your lights off, but not back on, make sure your bluetooth is turned on. If that doesn't fix it, try manually pairing your device to the Pi. Once it's paired once, it doesn't need to stay paired - just needs to be able to attempt a pairing.

contact info: ethan.seyl@gmail.com
