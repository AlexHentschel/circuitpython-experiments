A dedicated CircuitPython build for the `YD-RP2040` board by `VCC-GND Studio` exists:

https://circuitpython.org/board/vcc_gnd_yd_rp2040/

Installing CircuitPython on an RP2040-based microcontroller (like the `YD-RP2040`, Feather RP2040, or XIAO RP2040) using `Boot` and `Reset` buttons:
1. Enter Bootloader Mode
   1. Connect your RP2040 board to your computer via USB.
   2. Press and hold down the BOOTSEL (or BOOT) button.
   3. While still holding the BOOTSEL button, press and release the RESET (or RST) button.
   4. Release the BOOTSEL button.
   5. Your computer should now show a new USB drive named RPI-RP2.
2. Install CircuitPython:  
   Drag and drop the .uf2 file onto the RPI-RP2 drive. The board will automatically reboot.

WARNING: this does not work (or I am doing something incorrectly).

Modules included in `CircuitPython 10.1.4`:
```
_asyncio
_bleio
_bleio (HCI co-processor)
_eve
_pixelmap
adafruit_bus_device
adafruit_pixelbuf
aesio
alarm
analogbufio
analogio
array
atexit
audiobusio
audiocore
audiomixer
audiomp3
audiopwmio
binascii
bitbangio
bitmapfilter
bitmaptools
bitops
board
builtins
builtins.pow3
busdisplay
busio
busio.SPI
busio.UART
codeop
collections
countio
digitalio
displayio
epaperdisplay
errno
floppyio
fontio
fourwire
framebufferio
getpass
gifio
hashlib
i2cdisplaybus
i2cioexpander
i2ctarget
imagecapture
io
jpegio
json
keypad
keypad.KeyMatrix
keypad.Keys
keypad.ShiftRegisterKeys
keypad_demux
keypad_demux.DemuxKeyMatrix
locale
lvfontio
math
memorymap
microcontroller
msgpack
neopixel_write
nvm
onewireio
os
os.getenv
paralleldisplaybus
pulseio
pwmio
qrio
rainbowio
random
re
rgbmatrix
rotaryio
rp2pio
rtc
sdcardio
select
sharpdisplay
storage
struct
supervisor
synthio
sys
terminalio
tilepalettemapper
time
touchio
traceback
ulab
usb
usb_cdc
usb_hid
usb_host
usb_midi
usb_video
vectorio
warnings
watchdog
zlib
```