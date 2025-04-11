# NFC album player project

## Products
1. PN532 NFC Reader
    - I've tried a few, I haven't formed a strong preference on model.
    - Tested
2. Raspberry Pi
    - I've run the project on bot a Pi 4 1gb and a Pi Zero 2, recommend using the zero 2 as it's got plenty of resources to cover the need here.

## Steps to Setup

### Configure the hardware
Wire up nfc reader to pi with SPI.
```
PN532   <==>    Raspberry
5V      <==>    5V
GND     <==>    GND
SCK     <==>    SCKL
MISO	<==>    MISO
MOSI    <==>    MOSI
NSS     <==>    CE0
```
**NOTE** - Your PN532 board likely has SEL0 and SEL1 switches, or some other method to configure it's mode (SPI, I2C, UART). Make sure these are setup for SPI per your model's instrucations.

### Configure the OS and OS packages
Use Raspberry Pi Imager, or your preferred imager, to setup Pi OS Lite 64. I'm sure other OS options would work here but you're on your own if you take that path!

Update the packages.
`sudo apt update && sudo apt upgrade`

Enable SPI so we can communicate with the reader.
`sudo raspi-config` > Interfaces -> Enable SPI

SPI section of the second link (SPI Communication Instructions for Raspberry Pi)
-Substitute the official libnfc from github instead of this  - http://dl.bintray.com/nfc-tools/sources/libnfc-1.7.1.tar.bz2

Install pip

sudo apt install git
mkdir albumplayer
pull down github album-player project (git clone)
python3 -m venv my_venv
source ./my_venv/bin/activate
pip install -r requirements.txt

Test Registrar.py/Webapp.py

Install nfc module
pip install nfcpy
pip3 install adafruit-circuitpython-pn532

At this point the following should work 
```
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

# Create SPI connection
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D8)

# Create an instance of the PN532 class
pn532 = PN532_SPI(spi, cs_pin, debug=False)
ic, ver, rev, support = pn532.firmware_version

print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

print("Waiting for RFID/NFC card...")
while True:
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5)
    print(".", end="")
    # Try again if no card is available.
    if uid is None:
        continue
    print("Found card with UID:", [hex(i) for i in uid])
```

The above may have been dependent on another install from
git clone https://github.com/hoanhan101/pn532.git
and the corresponding 'make init' command listed there
-I'd try without it and do this as a last resort if needed

Setup code - pull down this repo, setup venv, pip install -r requirements.txt
Run Webapp.py and check http://album:3029
-Important: On the config tab set the player name for the sonos speaker you want to play albums to. This speaker is also used to play audio files that contain registration instructions.
Run AlbumPlayer.py and scan cards, go through the registration process

Copy albumweb and albumplayer service files to /etc/system/systemd/
-sudo systemctl enable name.service for each of them
-sudo systemctl daemon-reload

Ref:
https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html
http://wiki.sunfounder.cc/index.php?title=PN532_NFC_Module_for_Raspberry_Pi&ref=6doe1gqh2qgn

## Docker setup
Install 64 bit lite os

sudo apt update

sudo apt upgrade

sudo rasip-config > Interfaces > Enable SPI

curl -fsSL https://get.docker.com -o get-docker.sh

chmod +x get-docker.sh

sudo sh ./get-docker.sh

sudo usermod -aG docker [user_name]

exit and reconnect to ssh (needs to be done to re-validate your user's groups)

docker run --privileged --net=host dyonak/albumplayer:latest
- Verify this by going to hostname.local:3029 in a browser on the same network
- You should also see NFC cards getting read in the output if you put one near the reader

## Usage
All of this is assuming you've built some type of device that allows for an album with an NFC sticker tag, or other similar object with a NFC tag, to be placed so that it can be read by the NFC reader that you've configured. 

- Tag the album with the nfc tag (I like to place my tags about 1" inside the album cover, up 1" from the bottom of the album sleeve)
- Place the album on the "player" so the tag lines up with the reader
- You'll be prompted on the configured speaker to play the album on your configured speaker
- Open Sonos and play that album on the configured speaker
- The registration will poll several times ensuring that an album has been playing for over 10 seconds, if so it add this album to the database
- After registration the album begins playing
- You can remove the album at any time to stop playback

Once registered anytime you place that album back on the device it will begin to play.
