import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from touch_sensing import crosstalk_ratio, linear_to_db
for pitch in [4,6,8,10,12]:
    print(pitch, round(linear_to_db(crosstalk_ratio(pitch,5.0)),1), "dB")
# need ~9mm+ to clear -6dB
