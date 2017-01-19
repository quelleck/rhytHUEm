import configparser
import subprocess
import re
import os
from time import sleep
import datetime
from pysolar.solar import *
import requests
import json
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read('{}/config/rhythuem.ini'.format(dir_path))

def bridge_ip():
    meethue_page = requests.get('https://www.meethue.com/api/nupnp').json()
    logging.info("[do][bridge_ip] Bridge IP: {}".format(meethue_page))
    return meethue_page[0]['internalipaddress']


bridge_ip = bridge_ip()


def get_lights_in_group():
    json_data = groups_get_request()
    lights_used = json_data['lights']
    logging.debug("[do][get_lights_in_group] Lights in group: {}".format(lights_used))
    return lights_used


def groups_get_request():
    r = requests.get('http://{}/api/{}/groups/{}'.format(
        bridge_ip, config['DEFAULT']['HueApiKey'], config['DEFAULT']['LightGroup']))
    return r.json()


lights_used = get_lights_in_group()
number_of_lights_in_group = len(lights_used)


def blink_ready():
    put_request({'alert': 'select'})
    sleep(1.5)  # PAUSE FOR SLOW BRIDGE PERFORMANCE
    put_request({'alert': 'none'})
    logging.info("[do][blink_ready] Lights are ready")


def put_request(value):
    r = requests.put('http://{}/api/{}/groups/{}/action'.format(
        bridge_ip, config['DEFAULT']['HueApiKey'], config['DEFAULT']['LightGroup']),
                     data=json.dumps(value))


def lights_get_request(light):
    r = requests.get('http://{}/api/{}/lights/{}'.format(
        bridge_ip, config['DEFAULT']['HueApiKey'], light))
    return r.json()


def light_status(param):
    light_status = []
    for l in lights_used:
        data = str(lights_get_request(l))
        val = str(re.findall(r"'{}': [0-9]*".format(param), data))
        val = re.sub("\D", "", val)
        val = int(val)
        light_status.append(val)
    logging.debug("[do][light_status] Status of {}: {}".format(param, light_status))
    return light_status


def check_for_changes(old_values):
    logging.debug(
        "[do][check_for_changes] These are the old values composed of the CT and BRI lists: {}".format(
            old_values))  # LOG
    new_values = []
    new_values.insert(1, light_status('ct'))
    new_values.insert(2, light_status('bri'))
    logging.debug("[do][check_for_changes] New values addition: {}".format(new_values))
    ct_changes = compare_lists(old_values[0], new_values[0])
    bri_changes = compare_lists(old_values[1], new_values[1])
    if ct_changes or bri_changes:
        return True
    return False


def compare_lists(old_values, new_values):
    logging.debug("[do][compare_lists] Last saved values {}".format(old_values))
    logging.debug("[do][compare_lists] New values: {}".format(new_values))
    logging.debug("[do][compare_lists] Number of lights in group = {}".format(
        number_of_lights_in_group))
    i = 0
    for x in old_values:
        logging.debug("[do][compare_lists] Checking light {}".format(lights_used[i]))
        diff = x - new_values[i]
        logging.debug("[do][compare_lists] Difference between old and new values = {}".format(
            diff))
        if diff > 6 or diff < -6:
            logging.info("[do][compare_lists] Difference in light values: {}".format(diff))
            logging.info("[do][compare_lists] Manual changes detected on light {}...".format(x))
            return True
        i += 1
        logging.debug("No changes detected")
    return False


def check_for_device(device_list):
    num_devices = len(device_list)
    for device in device_list:
        output = subprocess.check_output(
            ['sudo', 'hcitool', 'name', device],
            stderr=subprocess.STDOUT)
        decoded_output = output.decode('utf-8')
        logging.debug("[do][check_for_device] Output: {}".format(decoded_output))
        if output:
            return True
        elif not output and num_devices > 1:
            num_devices -= 1
            print("Checking next device")
        else:
            return False


def sun_status():
    if config['DEFAULT']['SunAdjust'] is 'True':
        d = datetime.datetime.now()
        logging.debug("[do][sun_status] Current time: {}".format(d))
        altitude = get_altitude(float(config['DEFAULT']['Lon']), float(config['DEFAULT']['Lat']), d)
        logging.debug("[do][sun_status] Sun is {} degrees above/below the horizon".format(altitude))
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
    else:
        temp = 231
    return temp


def initial_adjust_lights():
    temp = sun_status()
    put_request({'on': True, 'bri': 254, 'ct': temp})
    sleep(12) # Wait for heartbeat


def adjust_lights():
    temp = sun_status()
    put_request({'bri': 254, 'ct': temp})
    sleep(12) # Wait for heartbeat


def home_wait():
    sleep(120)


def away_wait():
    sleep(20)


def wemo(on_off):
	if on_off:
		logging.debug("[do][wemo] Wemo recipe exists")
		requests.post('https://maker.ifttt.com/trigger/{}/with/key/{}'.format(
			on_off, config['WEMO']['IFTTTApiKey']))
	else:
		logging.debug("[do][wemo] No Wemo recipe in .ini")


#-----------------------------------------------------
def arrived_home():
    initial_adjust_lights()
    ct_settings = light_status('ct')
    bri_settings = light_status('bri')
    wemo(config['WEMO']['Off'])
    logging.info("[do][arrived_home] Arrived home... sleeping")
    home_wait()
    return ct_settings, bri_settings


def home(light_settings):
    if check_for_changes(light_settings):
        logging.debug("[do][home] Changes detected - do not update lights")
    else:
        adjust_lights()
    logging.info("[do][home] Home... sleeping")
    home_wait()


def left():
    put_request({'on': False})
    wemo(config['WEMO']['On'])
    logging.info("[do][left] Left... sleeping")
    away_wait()


def gone():
    logging.info("[do][gone] Gone... sleeping")
    away_wait()
