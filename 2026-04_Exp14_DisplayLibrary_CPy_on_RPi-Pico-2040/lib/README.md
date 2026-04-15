CircuitPython libraries and project modules.

Project modules:
  display.py             -- MakeCode-style display library for 8x8 WS2812b matrix

External libraries (.mpy, install via circup):
  neopixel.mpy           -- WS2812b NeoPixel driver
  adafruit_pixelbuf.mpy  -- pixel buffer base (dependency of neopixel)

Install external libs:
  /Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
    --path /Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040 \
    --board-id vcc_gnd_yd_rp2040 --cpy-version 10.1.4 \
    install neopixel
