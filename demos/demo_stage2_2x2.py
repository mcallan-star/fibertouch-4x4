"""Software demo of Stage-2 2x2 crosstalk/isolation (no hardware)."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
from touch_sensing import TouchPanel, crosstalk_ratio, linear_to_db, GRID

panel = TouchPanel(threshold=12)
amb = np.full((GRID, GRID), 8.0)
panel.calibrate([(np.full((GRID, GRID), 50.0), amb) for _ in range(20)])

leak = crosstalk_ratio(pitch_mm=9.0, isolation_len_mm=4.5)   # geometry
f = np.full((GRID, GRID), 50.0)
f[0, 0] += 45                       # touched
f[0, 1] += 45 * leak                # neighbour leak
f[1, 0] += 45 * leak
ch = panel.touch_change(f, amb)
iso_db = linear_to_db(ch[0, 1] / ch[0, 0])
print("touched %.1f  neighbour %.1f  isolation %.1f dB" % (ch[0, 0], ch[0, 1], iso_db))
print("PASS" if iso_db <= -6 else "FAIL (need >=6 dB isolation)")
