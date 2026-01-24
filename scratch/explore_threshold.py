import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from touch_sensing import TouchPanel, GRID
# just eyeballing where to put the threshold
p = TouchPanel(); p.calibrate([(np.full((GRID,GRID),50.0), np.full((GRID,GRID),8.0)) for _ in range(10)])
f = np.full((GRID,GRID),50.0); f[0,0]=90
print(p.touch_change(f, np.full((GRID,GRID),8.0))[0,0])  # ~40, so 10ish threshold is fine
