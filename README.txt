https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install-2

64-bit boards seem to work better

Download latest working image (2023-12-11 as of 10/27/24):
64-bit: https://downloads.raspberrypi.org/raspios_lite_arm64/images/
32-bit: https://downloads.raspberrypi.org/raspios_lite_armhf/images/


Setup Virtual Environment:

sudo apt update
sudo apt upgrade -y

sudo apt install -y python3-pyqt6 python3-pyqt6.qtqml python3-pyqt6.qtquick
sudo apt install -y libxcb-cursor-dev
sudo apt install -y pigpiod
sudo apt install -y git gh python3-pip

sudo apt install python3-venv
python -m venv --system-site-packages .venv

Activate Virtual Environment:

source .venv/bin/activate

or
#!/<path-to-venv>/bin/python
at top of scripts

PiTFT Installer Script

cd ~
pip install pyqt6
pip install --upgrade adafruit-python-shell click
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts


Console Mode Install Commands:

sudo -E env PATH=$PATH python3 adafruit-pitft.py --display=35r --rotation=90 --install-type=console

Or Interactive Install:

sudo -E env PATH=$PATH python3 adafruit-pitft.py


PWM Backlight Control:
Turn off STMPE control:
sudo sh -c 'echo "0" > /sys/class/backlight/soc\:backlight/brightness'

Turn on STMPE control (will stop PWM modulation):
sudo sh -c 'echo "1" > /sys/class/backlight/soc\:backlight/brightness'

Manipulate GPIO 18 to change backlighting:
gpio -g mode 18 pwm
gpio pwmc 1000
gpio -g pwm 18 100
gpio -g pwm 18 1023
gpio -g pwm 18 0





Obsolete:

Install WiringPi:
xxxIn Python:
xxxpip3 install wiringpi

In System:
From Source:
# fetch the source
sudo apt install git
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi

# build the package
./build debian
mv debian-template/wiringpi-3.0-1.deb .

# install it
sudo apt install ./wiringpi-3.0-1.deb

From Prebuilt:
wget https://github.com/WiringPi/WiringPi/releases//download/3.10/wiringpi_3.10_armhf.deb

# install a dpkg
sudo apt install ./wiringpi-3.0-1.deb


Install RPi.GPIO:
pip3 install RPi.GPIO

In script:
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT)
p = GPIO.PWM(18, 1000)  # (channel, frequency)
p.start(100.0)  # duty cycle (0.0-100.0)


Install Blinka:
sudo apt install --upgrade python3-setuptools
cd ~
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py

Will need following libraries in imports:
-board
-digitalio
-pwmio


Install GUI
pip install pygame-ce
pip install pygame_gui
sudo apt install -Y libegl-dev

