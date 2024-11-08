import pigpio

pi = pigpio.pi()

def cbf(gpio, level, tick):
    print(gpio, level, tick)


pi.set_mode(27, pigpio.INPUT)
pi.set_pull_up_down(27, pigpio.PUD_UP)

cb1 = pi.callback(27, pigpio.FALLING_EDGE, cbf)

message = input('press enter to quit\n\n')

cb1.cancel()
pi.set_pull_up_down(27, pigpio.PUD_OFF)

pi.stop()
