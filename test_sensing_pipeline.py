import numpy as np
from touch_sensing import TouchPanel, render_map, GRID


def _flat(v):
    return np.full((GRID, GRID), float(v))


def test_sw_s1_ambient_subtraction():   # SW-S1
    assert np.allclose(TouchPanel().signal(_flat(50), _flat(8)), 42.0)


def test_sw_s2_baseline_calibration():  # SW-S2
    p = TouchPanel()
    base = p.calibrate([(_flat(50 + k), _flat(8)) for k in range(5)])
    assert np.allclose(base, np.mean([42 + k for k in range(5)]))


def test_sw_s3_known_pattern():         # SW-S3
    p = TouchPanel(threshold=10)
    p.calibrate([(_flat(50), _flat(8)) for _ in range(10)])
    illum = _flat(50); illum[0, 2] = 80; illum[1, 1] = 75
    exp = np.zeros((GRID, GRID), bool); exp[0, 2] = exp[1, 1] = True
    assert np.array_equal(p.touch_map(illum, _flat(8)), exp)


def test_sw_s7_render_map():            # SW-S7
    m = np.zeros((GRID, GRID), bool); m[0, 2] = True
    assert render_map(m).splitlines()[0] == ". . X ."
