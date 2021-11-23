import os
import time
import requests
from sense_hat import SenseHat
sense = SenseHat()
sense.clear()

# Gets the cpu temp of computer
def get_cpu_temp():
    celcius = None
    temp = '/sys/devices/virtual/thermal/thermal_zone0/temp'
    if os.path.exists(temp):
        celcius = int(open(temp).read().strip()) / 1000
    return celcius

cpu_temp = get_cpu_temp()

TOKEN = "###############" #get your token at Ubidots
DEVICE = "RaspberryPi"
VARIABLE = "Temperature"
VARIABLE_2 = "Humidity"
VARIABLE_3 = "Pressure"

# Communicates with sensors and assign them to variables
def build_payload(variable_1, variable_2, variable_3):
    value_1 = sense.get_temperature()
    temp = value_1 - ((cpu_temp - value_1) / 2.7) + 0.5
    value_1 = round(temp, 1)
    value_2 = sense.get_humidity()
    value_3 = sense.get_pressure()
    payload = {variable_1: value_1, variable_2: value_2, variable_3: value_3}

    return payload

# Only communicates with the temperature sensor
def build_payload_2(variable_1):
    value_1 = sense.get_temperature()
    temp = value_1 - ((cpu_temp - value_1) / 2.7) + 0.5
    value_1 = round(temp, 1)
    payload = "Temperature: {}".format(value_1)   

    return payload

# Send a POST-request to Ubidots via API
def post_request(payload):
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False
    print("[INFO] request made properly, your device is updated")
    return True

# Defines which data is to be sent
def main():
        payload = build_payload(VARIABLE, VARIABLE_2, VARIABLE_3)

        print("[INFO] Attempting to send data...")
        post_request(payload)
        print("[INFO] data successfully sent!")
if __name__ == '__main__':
    while (True):
        main()
        payload = build_payload_2(VARIABLE)
        #sense.show_message(str(payload))
        print(str(payload))
        time.sleep(10)