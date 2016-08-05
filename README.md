# rhytHUEm

rhytHUEm is a customizable bluetooth proximity and color temperature (think f.lux) controller for Philips Hue lights built specifically for a Raspberry Pi.

#Features
- Bluetooth proximity detection to turn lights on/off. Use any bluetooth device, no pairing required (for most devices).
- Changes the color temperature of your lights throughout the day based on your location and the altitude of the Sun over the horizon. Smart enough to not override your settings if you make a change with another app. #HealthyCircadianRhythms
- Unlimited number of devices can be used for proximity detection.


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



contact info: ethan.seyl@gmail.com
