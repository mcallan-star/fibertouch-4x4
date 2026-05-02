import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
# sanity: illuminated pixel index == where we read. checking the row/col map
for i in range(16):
    print(i, i//4, i%4)
