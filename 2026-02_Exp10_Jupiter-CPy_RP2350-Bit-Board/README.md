# Experiment 10

**GOAL:** attempting a POC of CircuitPython via Jupyter Notebooks
https://learn.adafruit.com/circuitpython-with-jupyter-notebooks


Setup
- using RP2350 bit board 
- CircuitPython 10.1.3 for RaspberryPi Pico 2
  https://circuitpython.org/board/raspberry_pi_pico2/
-

Sub-goals:
- get LED working
- syntax completion?
- package and lib imports are also recognized for syntax completion




From Schematics: 
- Button A <-> GP0
- Button B <-> GP1

LED Matrix is exaclty like the microbit collum-row addressed:
           Top of board
    (0,0) (1,0) (2,0) (3,0) (4,0)

    (0,1) (1,1) (2,1) (3,1) (4,1)

    (0,2) (1,2) (2,2) (3,2) (4,2)

    (0,3) (1,3) (2,3) (3,3) (4,3)

    (0,4) (1,4) (2,4) (3,4) (4,4)
          Bottom of board
        with edge connector

using the GPIO lines as follows:

- LED column 0 <-> GP2
- LED column 1 <-> GP3
- LED column 2 <-> GP4
- LED column 3 <-> GP5
- LED column 4 <-> GP25

- LED row 0 <-> GP7
- LED row 1 <-> GP8
- LED row 2 <-> GP9
- LED row 3 <-> GP21
- LED row 4 <-> GP22

LED arranged such that Active is with Column High and Row Low
