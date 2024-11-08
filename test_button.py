import RPi.GPIO as GPIO


def button_callback(channel):
    print(channel, 'button was pushed')


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#while True:
#    if GPIO.input(13) == GPIO.LOW:
#        print('button pushed')

GPIO.add_event_detect(13, GPIO.FALLING, callback=button_callback)

message = input('press enter to quit\n\n')

GPIO.cleanup()
