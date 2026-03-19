import numpy as np
import pytest
from touch_sensing import TouchPanel, render_map, GRID


def _flat(v):
    return np.full((GRID, GRID), float(v))


def test_sw_s1_ambient_subtraction():   # SW-S1
    p = TouchPanel()
    illum, amb = _flat(50), _flat(8)
    assert np.allclose(p.signal(illum, amb), 42.0)


def test_sw_s2_baseline_calibration():  # SW-S2
    p = TouchPanel()
    frames = [(_flat(50 + k), _flat(8)) for k in range(5)]
    base = p.calibrate(frames)
    assert np.allclose(base, np.mean([42 + k for k in range(5)]))


def test_sw_s3_known_pattern():         # SW-S3
    p = TouchPanel(threshold=10)
    p.calibrate([(_flat(50), _flat(8)) for _ in range(10)])
    illum = _flat(50)
    illum[0, 2] = 80    # finger on (0,2)
    illum[1, 1] = 75    # finger on (1,1)
    tmap = p.touch_map(illum, _flat(8))
    expected = np.zeros((GRID, GRID), bool)
    expected[0, 2] = expected[1, 1] = True
    assert np.array_equal(tmap, expected)


def test_sw_s4_below_threshold_not_flagged():  # SW-S4
    p = TouchPanel(threshold=10)
    p.calibrate([(_flat(50), _flat(8)) for _ in range(10)])
    illum = _flat(50)
    illum[2, 2] = 55    # +5, under threshold
    assert not p.touch_map(illum, _flat(8)).any()


def test_sw_s5_detect_before_calibrate():   # SW-S5
    with pytest.raises(RuntimeError):
        TouchPanel().touch_change(_flat(50), _flat(8))


def test_sw_s6_frame_shape_guard():     # SW-S6
    with pytest.raises(ValueError):
        TouchPanel().signal(np.zeros((3, 3)), np.zeros((3, 3)))


def test_sw_s7_render_map():            # SW-S7
    m = np.zeros((GRID, GRID), bool)
    m[0, 2] = True
    assert render_map(m).splitlines()[0] == ". . X ."
