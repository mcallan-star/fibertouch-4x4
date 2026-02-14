"""Print the per-pixel link budget for the nominal geometry."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from touch_sensing import received_power_dbm
for L in (0.5, 1.0, 2.0):
    print("L=%.1fm  P_rx=%.2f dBm" %
          (L, received_power_dbm(0.0, 1.0, 0.6, L, 3.0)))
