import numpy as np
import pytest
from touch_sensing import (db_to_linear, linear_to_db, received_power_dbm,
                           crosstalk_ratio)


def test_sw_o1_db_roundtrip():          # SW-O1
    for db in [-20, -7.4, 0, 3.5, 12]:
        assert abs(linear_to_db(db_to_linear(db)) - db) < 1e-9


def test_sw_o2_link_budget():           # SW-O2
    # 0 dBm LED, 1 dB coupling x2, 0.6 dB/m x 2m x2, 3 dB finger -> -7.4 dBm
    p = received_power_dbm(0.0, 1.0, 0.6, 2.0, 3.0)
    assert abs(p - (-7.4)) < 1e-9


def test_sw_o3_longer_fiber_loses_more():   # SW-O3
    short = received_power_dbm(0, 1, 0.5, 1.0, 1)
    long = received_power_dbm(0, 1, 0.5, 3.0, 1)
    assert long < short


def test_sw_o4_crosstalk_falls_with_pitch():  # SW-O4
    vals = [crosstalk_ratio(p, 5.0) for p in [4, 8, 12, 16]]
    assert all(0 < v < 1 for v in vals)
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))


def test_sw_o5_input_guarding():        # SW-O5
    with pytest.raises(ValueError):
        crosstalk_ratio(-1, 5)
    with pytest.raises(ValueError):
        received_power_dbm(0, 1, 0.2, -1, 1)
