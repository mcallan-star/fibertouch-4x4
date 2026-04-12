import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from touch_sensing import TouchPanel, GRID
# show baseline + sigma after calibration, like the bench will do
rng=np.random.default_rng(3); p=TouchPanel()
p.calibrate([(np.full((GRID,GRID),50.0)+rng.normal(0,1.2,(GRID,GRID)), np.full((GRID,GRID),8.0)) for _ in range(20)])
print("baseline\n", p.baseline.round(1)); print("sigma\n", p.noise.round(2))
