"""Pi NoIR camera wrapper (picamera2). Locked exposure/gain, grayscale frames."""
try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None

import numpy as np


class Camera:
    def __init__(self, exposure_us=8000, gain=1.0):
        if Picamera2 is None:
            raise RuntimeError("picamera2 not available (run on a Pi)")
        self.cam = Picamera2()
        cfg = self.cam.create_still_configuration()
        self.cam.configure(cfg)
        self.cam.set_controls({"AeEnable": False, "AwbEnable": False,
                               "ExposureTime": int(exposure_us),
                               "AnalogueGain": float(gain)})
        self.cam.start()

    def frame(self):
        """2-D grayscale numpy array."""
        arr = self.cam.capture_array()
        if arr.ndim == 3:
            arr = arr[..., :3].mean(axis=2)
        return arr.astype(float)

    def close(self):
        self.cam.stop()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
