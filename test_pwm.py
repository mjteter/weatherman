#!/home/weatherman/my-venv/bin/python

import board
import time
import pwmio

led = pwmio.PWMOut(board.D18, frequency=5000, duty_cycle=0)

for jj in range(2):
    for ii in range (101):
        led.duty_cycle = int(ii * 65535 / 100)
        time.sleep(0.01)
    time.sleep(1)
    for ii in range(100, -1 , -1):
        led.duty_cycle = int(ii * 65535 / 100)
        time.sleep(0.01)
    time.sleep(1)
