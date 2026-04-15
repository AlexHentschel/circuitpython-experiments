# Experiment 12 -- Running the Adafruit AirLift firmware on generic ESP32

Context and long-term goal: Establish a **working ESP32-based WiFi coprocessor** connected to an RP2350 via SPI, functionally compatible with Adafruit’s AirLift (CircuitPython API), while using **cheap, replaceable ESP32 dev boards** for rapid iteration.

### Hardware

* D1 Mini ESP32 (ESP32-D0WD-V3)
* 4MB flash
* Generic unbranded module stating "ESP-32" and "WiFi+BT SoC Inside"

Comment:
ESP tools is installed in python environment 
```bash
source /Users/alex/Development/PythonVEs/MicroControllers/bin/activate
```

The following command indicates that the microcontroller's is connected to the host via port `/dev/tty.usbserial-0001`:
```bash
ls /dev/tty.*
```

Then, we can read out the microcontroller's hardware details via
```bash
esptool --port  /dev/tty.usbserial-0001 chip_id
```
and 
```bash
esptool --port /dev/tty.usbserial-0001 flash_id
```


### Tooling

* `esptool` 
* VS Code + pioarduino selected for development

## WiFi credentials (local)

For WiFi connect tests, credentials live in `include/secrets.h` (ignored by git).
Use `include/secrets.h.example` as a template.

---

## Flashing the AirLift (NINA) coprocessor firmware

To turn a generic ESP32 dev board into an AirLift-style SPI coprocessor (for CircuitPython’s `adafruit_esp32spi` later), flash the prebuilt Adafruit NINA firmware:

- See `docs/flashing-nina-fw.md`

---

## Immediate Goal (Phase 2)

> Get the ESP32 board reliably programmable and running basic firmware.

This validates:

* USB interface
* Flashing pipeline
* Runtime stability (power, regulator, RF)
* Development environment

---

## Next Steps

### 1. Set up development environment

* Install **pioarduino (VS Code extension)**
* Create project using:

  * Board: `esp32dev`
  * Framework: `arduino`

---

### 2. Flash a basic test program

Start with one of:

* Blink (sanity check)
* WiFi scan (preferred)

**Success criteria:**

* Board flashes without errors
* Serial monitor works
* WiFi scan runs reliably for several minutes

---

### 3. Validate hardware stability

Check for:

* No random resets
* No brownouts during WiFi activity

If issues appear:

* Add **220–470 µF capacitor** near board
* Improve power source

---

### 4. Decide firmware direction

Once stable:

#### Option A — Quick path

* Use **ESP-AT firmware**
* Communicate via UART (Lane A fallback)

#### Option B — Target path (recommended)

* Flash **AirLift / esp32spi firmware**
* Use SPI coprocessor model (Lane B)

---

### 5. Prepare SPI integration

Minimal wiring plan:

* SCK
* MOSI
* MISO
* CS
* RESET (recommended)
* Optional: BUSY/IRQ

No tri-state buffer needed initially (dedicated SPI bus)
