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

Enable SPI so we can communicate with the reader.

`sudo raspi-config` > Interfaces -> Enable SPI

Update the packages.

`sudo apt update && sudo apt upgrade`

### Install the OS dependencies
```
sudo apt install -y build-essential python3-dev libxml2-dev gcc g++ libxml2 libxslt1-dev libusb-dev libpcsclite-dev libffi-dev python3-setuptools python3-pip git

mkdir libnfc && cd libnfc
wget https://github.com/nfc-tools/libnfc/releases/download/libnfc-1.8.0/libnfc-1.8.0.tar.bz2
tar -xf libnfc-1.8.0.tar.bz2
./libnfc-1.8.0/configure --prefix=/usr --sysconfdir=/etc
make
make install
```

After completing the above package and libnfc installs you'll need to create the following file at:

`/etc/nfc/libnfc.conf`

```
# Allow device auto-detection (default: true)
# Note: if this auto-detection is disabled, user has to set manually a device
# configuration using file or environment variable
allow_autoscan = true

# Allow intrusive auto-detection (default: false)
# Warning: intrusive auto-detection can seriously disturb other devices
# This option is not recommended, user should prefer to add manually his device.
allow_intrusive_scan = false

# Set log level (default: error)
# Valid log levels are (in order of verbosity): 0 (none), 1 (error), 2 (info), 3 (debug)
# Note: if you compiled with --enable-debug option, the default log level is "debug"
log_level = 1

# Manually set default device (no default)
# To set a default device, you must set both name and connstring for your device
# Note: if autoscan is enabled, default device will be the first device available in device list.
device.name = "_PN532_SPI"
device.connstring = "pn532_spi:/dev/spidev0.0:500000"
#device.name = "_PN532_I2c"
#device.connstring = "pn532_i2c:/dev/i2c-1"
```

### Configure python/pip/repo

The following will grab this repo, create a directory to store it in and then setup a python virtual environment that includes all of the required modules. This project has a lot of modules and I highly recommend using the virtual environment so as not to clutter up your global modules.
```
git clone https://github.com/dyonak/Album-Player-Standalone
cd Album-Player-Standalone
python3 -m venv myvenv
source ./myvenv/bin/activate
pip install -r requirements.txt
```

**NOTE** - You'll notice your terminal is now prefixed with (my_venv), this indicates you're working in the python virtual environment. To deactivate this simply use `deactivate`. Repeat the `source ./myvenv/bin/activate` to re-enter the venv.

## Configuration of the Album Player

Run `python3 Webapp.py` and check http://<hostname/IP>:3029

**NOTE** - On the config tab set the player name for the Sonos speaker you want to play albums to. This speaker is also used to play audio files that contain registration instructions. You'll also need to set the service name (currently only "spotify" is supported), the service_api_id and service_api_secret. You can create an app and get these last two configuration items at developer.spotify.com. Create an account, go to your Dashboard, click the button that says "Create app".

After providing all of the information in the config page of the webapp you'll want to create and enable two services to run on the system. 

1. albumweb.service
    - Hosts the page just used to configure the app but also shows your currently registered albums, allows you to delete albums removed from your collection, and shares some metrics about your "plays" for each album.
2. albumplayer.service
    - Continually scans for new albums (nfc cards) being read and plays them or, in cases where the album does not exist in your collection, begins the registration process.

To make sure these are running as services, starting automatically on bootup, follow these instructions.
`cp albumweb.service /etc/systemd/system/albumweb.service`
`cp albumweb.service /etc/systemd/system/albumplayer.service`
`sudo systemctl enable albumweb.service`
`sudo systemctl enable albumplayer.service`
`sudo systemctl start albumweb.service`
`sudo systemctl start albumplayer.service`
`sudo systemctl daemon-reload`

## Usage
All of this is assuming you've built some type of stand that allows for an album with an NFC sticker tag, or other similar object with a NFC tag, to be placed so that it can be read by the NFC reader that you've configured. 

1. Tag the album with the nfc tag (I like to place my tags about 1" inside the album cover, up 1" from the bottom of the album sleeve)
2. Place the album on the "player" so the tag lines up with the reader
3. You'll be prompted on the configured speaker to play the album on your configured speaker
4. Open Sonos and play that album on the configured speaker
5. The registration will poll several times ensuring that an album has been playing for over 10 seconds, if so it add this album to the database
6. After registration the album begins playing
7. You can remove the album at any time to stop playback

Once an album has been registered you can place that album on the player at anytime to begin playback on your configured Sonos speaker.

Enjoy!
