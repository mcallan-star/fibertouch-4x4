# Raspberry Pi drivers

These only run on the Pi (need `picamera2` + the Adafruit PCA9685 stack). The parent modules (`touch_sensing.py`, `fiber_propagation.py`) and the notebooks run anywhere.

## Wiring
- PCA9685 on I2C (SDA/SCL), each channel -> one IR LED via a current-limit resistor.
- Pi NoIR camera on the CSI port, aimed at the RX receiver grid in the dark box.

## Setup
```bash
sudo raspi-config        # enable I2C + camera
pip install -r requirements.txt
```

## Calibrate ROIs + run
Find the 4x4 receiver grid in a captured frame, then:
```bash
python run_touch_map.py --x0 120 --y0 90 --dx 40 --dy 40 --box 12
```
Keep the surface clear while it calibrates the baseline, then touch away.
