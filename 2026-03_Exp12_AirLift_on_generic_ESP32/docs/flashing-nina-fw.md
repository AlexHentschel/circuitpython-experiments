# Flashing Adafruit AirLift (NINA) firmware onto a generic ESP32

This project’s long-term goal is to run Adafruit’s **ESP32SPI / AirLift-style NINA firmware** on a cheap ESP32 dev board, so an RP2350 (later) can talk to it over SPI.

These steps flash the **prebuilt “all-in-one”** firmware from Adafruit’s `nina-fw` releases directly onto the ESP32.

## 0) Pick the right prebuilt binary

Download from the latest Adafruit release:

- Release page: https://github.com/adafruit/nina-fw/releases/latest
- For a classic ESP32 (ESP32-D0WD / WROOM-32 class):
  - `NINA_ADAFRUIT-esp32-<version>.bin` (recommended for normal use)
  - `NINA_ADAFRUIT-esp32-<version>_Debug.bin` (helpful during bring-up; prints more over UART)

These are “all-in-one” images intended to be flashed at offset `0x0`.

## 1) Flash using Adafruit WebSerial ESPTool (recommended)

Prereqs:

- Use **Chrome** or **Edge** (WebSerial is required).
- Disconnect other USB serial devices to avoid picking the wrong port.

Steps:

1. Open the flasher: https://adafruit.github.io/Adafruit_WebSerial_ESPTool/
2. Select **115200** baud in the top-right.
3. Click **Connect**, then select the ESP32 serial port (on macOS typically `/dev/cu.usbserial-*` or `/dev/cu.usbmodem*`).
4. In the flashing UI:
   - Set **Offset** to `0x0`
   - Choose the `NINA_ADAFRUIT-esp32-...bin` file you downloaded
5. Click **Program**.
6. When it finishes, press **Reset** on the ESP32.

If it won’t connect / can’t sync:

- Put the ESP32 into ROM bootloader mode manually:
  - Hold **BOOT** (GPIO0 low), tap **RESET**, then release **BOOT**.
  - Then click **Connect** again and retry.

## 2) Flash using `esptool.py` (CLI fallback)

If WebSerial isn’t cooperating, you can flash from a terminal.

Example (macOS):

```bash
python3 -m pip install --user esptool

# Identify your port first (example shown)
ls /dev/cu.*

# Flash the all-in-one image at offset 0
esptool.py --chip esp32 --port /dev/cu.usbserial-0001 --baud 460800 write_flash 0x0 NINA_ADAFRUIT-esp32-3.3.0.bin
```

Notes:

- If `--baud 460800` is flaky, retry with `--baud 115200`.
- This overwrites whatever you previously flashed via PlatformIO/Arduino.

## 3) “Out of the box” SPI + handshake pin mapping (stock firmware)

If you flash Adafruit’s **stock** `NINA_ADAFRUIT-esp32` image, it expects a specific ESP32-side wiring for the SPI slave and ready/handshake pins.

From Adafruit’s `nina-fw` `boards/esp32/board.h`:

- `AIRLIFT_MOSI` = GPIO14  (host MOSI → ESP32 GPIO14)
- `AIRLIFT_MISO` = GPIO23  (host MISO ← ESP32 GPIO23)
- `AIRLIFT_SCK`  = GPIO18  (host SCK  → ESP32 GPIO18)
- `AIRLIFT_CS`   = GPIO5   (host CS   → ESP32 GPIO5)
- `AIRLIFT_BUSY` = GPIO33  (ESP32 “ready/busy” output → host input)
- GPIO0 is also used by the firmware as an IRQ-style signal for data-ready events.

You do **not** need to decide the RP2350-side pins yet; just ensure your ESP32 board breaks out the ESP32 GPIOs above.

## 4) What to expect after flashing

- NINA firmware is meant to be controlled over SPI by a host; it may appear “quiet” on serial in non-debug builds.
- Your existing PlatformIO Arduino sketch will no longer run until you re-flash it.

