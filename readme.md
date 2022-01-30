# Python wrapper for Vocore Screens

This repo includes some python helper scripts to easily interface with the [VoCore Screen v2](https://vocore.io/screen.html) without the need of any additional drivers.
Internally PyUSB is used, which in turn uses libusb.

For now this has only been tested with the 4" VoCore Screen v2 (with touch). This should also work with the 4.3" version.
As the 5" version has a slightly higher resolution, this will most likely not work. Adjusting the `FRAME_SIZE` in `image.py` and the command in `screen.VocoreScreen._write_start` could possible fix this.

For usage check the `example.py` - it should be pretty straightforward.


## Working features
* Setting screen brightness
* Sending images to the screen
* Thus, setting arbitrary pixels to colors of choosing

## Not working (yet)
* Getting touch events (Should be interrupt endpoint at 0x81 with a length of 128 bytes)

# Getting started
* Make sure to install the pipenv environment (`pipenv install`)
### Linux
* Make sure your screen in plugged in
* Make sure `libusb` is installed
* If you want to use the scripts as non-root, make sure to add a rule to /etc/udev/rules.d/
* You are good to go 🎉

### Windows
* Download and install the **LibUSBk** driver from the [VoCore Homepage](https://vocore.io/screen.html)
* That's it 😀