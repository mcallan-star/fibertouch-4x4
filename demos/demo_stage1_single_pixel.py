"""Software demo of the Stage-1 single-pixel check (no hardware).
Synthesizes touched/untouched signals + noise, prints SNR."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
from touch_sensing import TouchPanel, GRID

rng = np.random.default_rng(1)
panel = TouchPanel(threshold=12)
amb = np.full((GRID, GRID), 8.0)
untouched = [(np.full((GRID, GRID), 50.0) + rng.normal(0, 1.5, (GRID, GRID)), amb)
             for _ in range(20)]
panel.calibrate(untouched)

changes = []
for _ in range(10):                       # 10 touch cycles on pixel (0,0)
    f = np.full((GRID, GRID), 50.0) + rng.normal(0, 1.5, (GRID, GRID))
    f[0, 0] += 45                         # finger
    changes.append(panel.touch_change(f, amb)[0, 0])
snr = np.mean(changes) / panel.noise[0, 0]
print("mean touch_change %.1f  noise sigma %.2f  SNR %.1f" %
      (np.mean(changes), panel.noise[0, 0], snr))
print("PASS" if snr >= 5 else "FAIL")
