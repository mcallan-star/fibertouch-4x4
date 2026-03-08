import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from touch_sensing import TouchPanel, GRID
rng=np.random.default_rng(0); p=TouchPanel()
p.calibrate([(np.full((GRID,GRID),50.0)+rng.normal(0,1.5,(GRID,GRID)), np.full((GRID,GRID),8.0)) for _ in range(50)])
print("sigma", p.noise.mean())  # noise floor for snr
