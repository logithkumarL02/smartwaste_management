# SmartWaste — Hardware Integration Guide

## Current State: Simulation

The system runs entirely in software. `SimulationSortingDevice` handles all sort commands by logging them with visual indicators. No physical hardware is required.

---

## Hardware Abstraction Design

```
classify() → ClassificationResult
                      ↓
         SortingDevice.sort(command)
                      ↓
     ┌────────────────┴──────────────────┐
     │                                   │
SimulationDevice         RaspberryPiDevice / ESP32Device / RoboticArmDevice
(current)                     (future — plug in here)
```

The classification pipeline and API never reference hardware-specific code. Only `get_sorting_device()` needs to change when upgrading hardware.

---

## Adding Raspberry Pi Support

1. Wire GPIO pins to your servo/stepper controllers.

2. Create `backend/app/hardware/raspberry_pi.py`:

```python
import RPi.GPIO as GPIO
from .base import SortingDevice

BIN_PINS = {
    "SORT_PLASTIC":  17,
    "SORT_METAL":    27,
    "SORT_GLASS":    22,
    "SORT_PAPER":    23,
    "SORT_ORGANIC":  24,
    "SORT_EWASTE":   25,
    "SORT_TEXTILE":  8,
    "SORT_OTHER":    7,
    "MANUAL_REVIEW": None,
}

class RaspberryPiSortingDevice(SortingDevice):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in BIN_PINS.values():
            if pin: GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def sort(self, command: str):
        pin = BIN_PINS.get(command)
        if pin is None:
            return True, "Manual review flagged."
        GPIO.output(pin, GPIO.HIGH)
        import time; time.sleep(0.5)
        GPIO.output(pin, GPIO.LOW)
        return True, f"GPIO pin {pin} triggered for {command}"

    def get_mode(self): return "raspberry_pi"
    def is_available(self): return True
```

3. Register in `controller.py` and set `HARDWARE_MODE=raspberry_pi`.

---

## Adding ESP32 Support

The ESP32 receives commands over WiFi (HTTP or MQTT).

```python
import requests
from .base import SortingDevice

class ESP32SortingDevice(SortingDevice):
    def __init__(self, esp32_ip: str):
        self.base_url = f"http://{esp32_ip}"

    def sort(self, command: str):
        try:
            r = requests.post(f"{self.base_url}/sort", json={"cmd": command}, timeout=3)
            return r.ok, r.json().get("message", "")
        except Exception as e:
            return False, str(e)

    def get_mode(self): return "esp32"
    def is_available(self):
        try:
            requests.get(f"{self.base_url}/ping", timeout=2)
            return True
        except:
            return False
```

---

## Edge Inference (TFLite on Raspberry Pi)

For lower latency on edge devices, convert the model:

```python
import tensorflow as tf

model = tf.keras.models.load_model("model/waste_classifier.keras")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]   # INT8 quantization
tflite_model = converter.convert()
with open("model/waste_classifier.tflite", "wb") as f:
    f.write(tflite_model)
```

Run on Pi using `tflite-runtime`:
```bash
pip install tflite-runtime
```

---

## Future Robotic Arm Workflow

```
Camera
  ↓
Waste Detection (OpenCV bounding box)
  ↓
Classification (CNN)
  ↓
Confidence Check
  ↓  ← below threshold → MANUAL_REVIEW (arm holds, human decides)
Sorting Controller
  ↓
Hardware Command
  ↓
Robotic Arm (ROS2 / custom serial protocol)
  ↓
Target Bin
```

**Critical safety rule:** Uncertain predictions (`is_uncertain=True`) must **never** automatically trigger physical hardware. They must route to `MANUAL_REVIEW` and wait for human confirmation.
