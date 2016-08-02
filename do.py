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
    

def bridge_ip():
    meethue_page = requests.get('https://www.meethue.com/api/nupnp').json()
    print("Bridge IP: {}".format(meethue_page[0]['internalipaddress']))  # LOG
    return meethue_page[0]['internalipaddress']

bridge_ip = bridge_ip()

def check_for_bluetooth():
    output = False
    while output == False:
        output = subprocess.check_output(['ps', '-A'])
        output = output.decode("utf-8")
        if 'bluetoothd' in output:
            print("Bluetooth is running")  # LOG
            put_request({'alert': 'select'})
            sleep(1.5)  #  PAUSE FOR SLOW BRIDGE PERFORMANCE
            put_request({'alert': 'none'})
            return True
        else:
            print("Bluetooth is not running... waiting")  # LOG
            return False


def put_request(value):
    r = requests.put('http://{}/api/{}/groups/{}/action'.format(
        bridge_ip, config.hue_api_key, config.light_group),
                     data=json.dumps(value))
    print(r.json())  # LOG


def groups_get_request():
    r = requests.get('http://{}/api/{}/groups/{}'.format(bridge_ip, config.hue_api_key, config.light_group))
    return r.json()


def lights_get_request(light):
    r = requests.get('http://{}/api/{}/lights/{}'.format(bridge_ip,
                                                         config.hue_api_key,
                                                         light))
    return r.json()


def get_lights_in_group():
    json_data = groups_get_request()
    lights_used = json_data['lights']
    print("Lights used: {}".format(lights_used))  # LOG
    return lights_used


def light_status(param):
    light_status = []
    lights_used = get_lights_in_group()
    for l in lights_used:
        data = str(lights_get_request(l))
        val = str(re.findall(r"'{}': [0-9]*".format(param), data))
        val = re.sub("\D", "", val)
        val = int(val)
        light_status.append(val)
    print(light_status)  # LOG
    return light_status


def check_for_changes(old_values):
    print("These are the old values composed of the CT and BRI lists: {}".format(old_values))  # LOG
    new_values = []
    new_values.insert(1, light_status('ct'))
    new_values.insert(2, light_status('bri'))
    print("New values addition: {}".format(new_values))  # LOG
    ct_changes = compare_lists(old_values[0], new_values[0])
    bri_changes = compare_lists(old_values[1], new_values[1])
    if ct_changes or bri_changes:
        return True
    return False
    
    
def compare_lists(old_values, new_values):
    print("CL Old: {}".format(old_values))  # LOG
    print("CL New: {}".format(new_values))  # LOG
    lights_in_group = get_lights_in_group()
    number_of_lights_in_group = len(lights_in_group)
    print("Number of lights in group = {}".format(number_of_lights_in_group))  # LOG
    i = 0
    for x in old_values:
        print("Checking light {}".format(lights_in_group[i]))  # LOG
        diff = x - new_values[i]
        print("diff = {}".format(diff))  # LOG
        if diff > 6 or diff < -6:
            print("Manual changes detected...")  # LOG
            return True
        print("No changes detected")  # LOG
        i += 1
    return False

        
        
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
    elif altitude >= -18 and altitude < -5:
        temp = 500
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


def initial_adjust_lights():
    temp = sun_status()
    put_request({'on': True, 'bri': 254, 'ct': temp})


def adjust_lights():
    temp = sun_status()
    put_request({'bri': 254, 'ct': temp})


#def light_status():
    

def home_wait():
    sleep(5)  #  REMINDER TO CHANGE THIS BACK


def away_wait():
    sleep(5)  #  REMINDER TO CHANGE THIS BACK


#-----------------------------------------------------
def arrived_home():
    initial_adjust_lights()
    print("Arrived home... sleeping")  # LOG
    ct_settings = light_status('ct')
    bri_settings = light_status('bri')
    home_wait()
    return ct_settings, bri_settings


def home(light_settings):
    if check_for_changes(light_settings):
        print("Changes detected - do not update lights")  # LOG
    else:
        adjust_lights()
    print("Home... sleeping")  # LOG
    home_wait()


def left():
    put_request({'on': False})
    print("Left... sleeping")  # LOG
    away_wait()


def gone():
    print("Gone... sleeping")  # LOG
    away_wait()
