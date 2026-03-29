import numpy as np
from touch_sensing import render_map
def test_render_all_dots():
    assert render_map(np.zeros((4,4),bool)).splitlines()[3] == ". . . ."
def test_render_full_row():
    m=np.zeros((4,4),bool); m[0,:]=True
    assert render_map(m).splitlines()[0] == "X X X X"
