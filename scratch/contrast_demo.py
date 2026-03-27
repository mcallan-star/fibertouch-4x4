import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from touch_sensing import TouchPanel, GRID
p=TouchPanel(); p.calibrate([(np.full((GRID,GRID),50.0), np.full((GRID,GRID),8.0)) for _ in range(10)])
f=np.full((GRID,GRID),50.0); f[0,0]=80
print("contrast", p.normalized_signal(f, np.full((GRID,GRID),8.0))[0,0])  # touch_change/baseline
