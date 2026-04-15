
# Board Preparation

Before you start using the CircuitPython_Kernel, you'll need a board running CircuitPython. If you're not sure if
the board plugged into your computer is running CircuitPython, check your file explorer for a drive named `CIRCUITPY`

## Designed for CircuitPython (SAMD21, SAMD51 and RP2040, NXP iMXRT1062)

### Boards Supported:

 - [Circuit Playground Express](https://www.adafruit.com/product/3333)
 - [Feather M0](https://www.adafruit.com/product/3403)
 - [Trinket M0](https://www.adafruit.com/product/3500)
 - [Metro M0 Express](https://www.adafruit.com/product/3505)
 - [Gemma M0](https://www.adafruit.com/product/3501)
 - [ItsyBitsy M0](https://www.adafruit.com/product/3727)

 - [Metro M4 ]( https://www.adafruit.com/product/3382)
 - [ItsyBitsy M4](https://www.adafruit.com/product/3727)

 - [Raspberry Pi Pico RP2040](https://www.adafruit.com/product/4864)
 - [PJRC Teensy 4.1](https://www.adafruit.com/product/4622)

### Installing CircuitPython Firmware

- Download the [CircuitPython Firmware (.uf2 file) from the CircuitPython Repo](https://github.com/adafruit/circuitpython/releases)
- Plug in board and double click the **reset** button to enter bootloader mode.
- Drag and drop the \*.uf2 CircuitPython file to the USB drive.
- If you see the `CIRCUITPY` as the new name of the USB drive, you're ready to go.


## Adafruit Feather Huzzah ESP8266

While they do work with CircuitPython_Kernel, ESP8266-based boards require a different type of installation and configuration
from the boards designed for circuitpython.

### Installing CircuitPython Firmware

- `python3 -m pip install esptool`
- Download the [CircuitPython Firmware (.bin file) from the CircuitPython Repo](https://github.com/adafruit/circuitpython/releases)
- Install the [SiLabs CP210x driver](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers)
- Erase flash `python3 esptool.py --port /path/to/ESP8266 erase_flash`
- Load firmware: `esptool.py --port /path/to/ESP8266 --baud 460800 write_flash --flash_size=detect 0 firmware.bin`
- Press reset or unplug/plug the board.

### Access the REPL

Use `screen` program:

    screen <device> 115200

## PJRC Teensy 4.1

The Teensy line of microcontrollers have a different installation to the standard circuitpython installation, requiring a program called Teensy Loader and a hex file.

### Installing CircuitPython Firmware

- Download the Teensy Loader Application: https://www.pjrc.com/teensy/loader.html
- Install the loader following the guide for your specific operating system.
- Download the [CircuitPython Firmware (.hex file) from the CircuitPython Website](https://circuitpython.org/board/teensy41/)
- Once the Teensy Loader is downloaded, press the onboard push button on the Teensy, this places the teensy in the halfkay bootlader mode.
- Open the Teensy Loader Application and select the left most button and upload the downloaded .hex file.
- Unplug and plug the Teensy back in and you are ready to go.

## ampy

- Install ampy `python3 -m pip install adafruit-ampy`
- To get options for listing files and moving files: `ampy --help`
