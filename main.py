#!/home/weatherman/.venv/bin/python

import socket
from turtledemo.penrose import start

import requests

import logging

import threading
import queue

from psychrometric import psych
from datetime import datetime, timedelta
from time import sleep, time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
    B_RPI_GPIO_EXISTS = False
except RuntimeError:
    GPIO = None
    B_RPI_GPIO_EXISTS = False
else:
    GPIO.setmode(GPIO.BOARD)
    B_RPI_GPIO_EXISTS = True

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
# logger levels: NOTSET   =  0
#                DEBUG    = 10
#                INFO     = 20
#                WARN     = 30
#                ERROR    = 40
#                CRITICAL = 50


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def get_noaa_grid(api_header, lat_long):
    response = {'properties': {'gridId': 'PHI', 'gridX': 38, 'gridY': 78}}
    try:
        response = requests.get('https://api.weather.gov/points/' + str(lat_long[0]) + ',' + str(lat_long[1]),
                                headers=api_header).json()
    except TimeoutError:  # , ConnectTimeoutError:
        _logger.error('No response to grid request.  Grid set to default of (38,78)')
    finally:
        resp_grids = (response['properties']['gridId'] + '/' + str(response['properties']['gridX']) + ',' +
                      str(response['properties']['gridY']))

    return resp_grids


class NOAAForecastThread(threading.Thread):
    # Thread to routinely make requests to weather.gov for forecast and current data

    def __init__(self, api_header, noaa_grid, noaa_to_bank_queue, loop_time=300):
        threading.Thread.__init__(self, daemon=True)  # init thread, daemon=True means thread will die with main program
        self.api_header = api_header
        self.noaa_hourly_url = 'https://api.weather.gov/gridpoints/' + noaa_grid + '/forecast/hourly'
        self.noaa_to_bank_queue = noaa_to_bank_queue
        self.loop_time = loop_time

    def run(self):
        start_time = time()
        sleep(0.1)

        try:
            response = requests.get(self.noaa_hourly_url, headers=self.api_header).json()
        except TimeoutError:
            response = None

        print(response)

        while True:
            cur_time = time()

            if cur_time - start_time > self.loop_time:
                try:
                    response = requests.get(self.noaa_hourly_url, headers=self.api_header).json()
                except TimeoutError:
                    response = None




def main(api_header, api_grids):

    noaa_to_bank_queue = queue.Queue()
    noaa_forecast = NOAAForecastThread(api_header, api_grids)

    _logger.info('Start NOAA Forecast thread')
    noaa_forecast.start()

    sleep(10)
    _logger.info('Ending program')
    return


if __name__ == '__main__':
    socket.setdefaulttimeout(3)

    default_lat_long = (40.0415, -75.4841)  # default latitude and longitude (me!)
    default_header = {'User-Agent': 'Matt Teter, mteter9530@gmail.com', 'accept': 'application/geo+json'}

    default_grids = get_noaa_grid(default_header, default_lat_long)

    local_ip = get_ip()
    local_name = socket.gethostname()

    main(default_header, default_grids)
