import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from touch_sensing import render_map
import numpy as np
m = np.zeros((4,4),bool); m[1,1]=m[2,3]=True
print(render_map(m))   # quick look
