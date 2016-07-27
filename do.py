import config
import subprocess
import re
from time import sleep
import datetime
from pysolar.solar import *
import requests
import json
import pysolar


def initial_wait():
    print("sleeping 25")
    sleep(25)


def check_for_bluetooth():
    output = False
    while output == False:
        output = subprocess.check_output(['ps', '-A'])
        output = output.decode("utf-8")
        if 'bluetoothd' in output:
            print("Bluetooth is running")  # LOG
            put_request({'alert': 'select'})
            sleep(1)  #  API CALLS FOR 1 GROUP REQUEST PER SEC MAX - RESET ALERT TO NONE
            put_request({'alert': 'none'})
            return True
        else:
            print("Bluetooth is not running... waiting")  # LOG
            return False


def bridge_ip():
    meethue_page = requests.get('https://www.meethue.com/api/nupnp').json()
    return meethue_page[0]['internalipaddress']


def put_request(value):
    r = requests.put('http://{}/api/{}/groups/0/action'.format(
        bridge_ip(), config.hue_api_key),
                     data=json.dumps(value))
    print(r.json())  # LOG


def check_for_device(device_list):
    num_of_devices = len(device_list)
    index = 0
    while num_of_devices > 0:
        device = device_list[index]
        print("Checking for device {}".format(device))  # LOG
        attempts = 0
        while attempts < 2:
            output = subprocess.check_output(
                ["sudo", "rfcomm", "connect", "0", device],
                stderr=subprocess.STDOUT)
            decode = output.decode("utf-8")
            print(decode)  # LOG
            away = re.search("Host", decode)
            if away:
                attempts += 1
            else:
                return True
        num_of_devices -= 1
        index += 1
    return False


def sun_status():
    d = datetime.datetime.now()
    print("Current time: {}".format(d))
    altitude = get_altitude(config.lon, config.lat, d)
    print("Sun is {} degrees above/below the horizon".format(altitude))
    if altitude <= -18:
        temp = 500
    elif altitude >= -18 and altitude < -13:
        temp = 430
    elif altitude >= -13 and altitude < -10:
        temp = 400
    elif altitude >= -10 and altitude < -7:
        temp = 370
    elif altitude >= -7 and altitude < -5:
        temp = 350
    elif altitude >= -5 and altitude < -2:
        temp = 320
    elif altitude >= -2 and altitude < 0:
        temp = 300
    elif altitude >= 0 and altitude < 5:
        temp = 280
    elif altitude >= 5 and altitude < 10:
        temp = 270
    elif altitude >= 10 and altitude < 20:
        temp = 254
    elif altitude >= 20 and altitude < 30:
        temp = 245
    elif altitude >= 30 and altitude < 40:
        temp = 234
    elif altitude >= 40 and altitude <= 90:
        temp = 153
    return temp


def adjust_lights():
    temp = sun_status()
    put_request({'on': True, 'bri': 254, 'ct': temp})

#-----------------------------------------------------
def arrived_home():
    adjust_lights()
    print("Arrived home... sleeping")  # LOG
    sleep(180)


def home(temp):
    adjust_lights()
    print("Home... sleeping")  # LOG
    sleep(180)


def left():
    put_request({'on': False})
    print("Left... sleeping")  # LOG
    sleep(17)


def gone():
    print("Gone... sleeping")  # LOG
    sleep(17)
