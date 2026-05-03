"""Scan LEDs one at a time, build (illuminated, ambient) 4x4 brightness arrays."""
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from touch_sensing import TouchPanel, render_map, GRID   # noqa: E402

N = GRID * GRID


class Scanner:
    def __init__(self, leds, camera, recmap, settle_s=0.01, level=1.0):
        self.leds = leds
        self.camera = camera
        self.recmap = recmap
        self.settle_s = settle_s
        self.level = level

    def scan(self):
        self.leds.all_off()
        time.sleep(self.settle_s)
        ambient = self.recmap.read(self.camera.frame())
        illum = np.zeros((GRID, GRID), dtype=float)
        for i in range(N):
            self.leds.on(i, self.level)
            time.sleep(self.settle_s)
            reading = self.recmap.read(self.camera.frame())
            illum[i // GRID, i % GRID] = reading[i // GRID, i % GRID]
            self.leds.off(i)
        return illum, ambient

    def calibrate(self, panel, frames=20):
        frames_list = [self.scan() for _ in range(frames)]
        return panel.calibrate(frames_list)
