import numpy as np
import pytest
from fiber_propagation import (gaussian_pulse, sech_pulse, dispersion_length,
                               fundamental_soliton_power, soliton_order,
                               energy, rms_width, split_step_fourier)


def _grid(n=4096, span=80.0):
    return np.linspace(-span / 2, span / 2, n)


def test_sw_p1_dispersive_broadening():     # SW-P1
    t = _grid()
    T0, beta2 = 1.0, -1.0
    A0 = gaussian_pulse(t, T0=T0)
    LD = dispersion_length(T0, beta2)
    z = 2.0 * LD
    A = split_step_fourier(A0, t, z, 2000, beta2=beta2)
    expected = rms_width(A0, t) * np.sqrt(1 + (z / LD) ** 2)
    assert abs(rms_width(A, t) - expected) / expected < 0.02


def test_sw_p2_soliton_invariance():        # SW-P2
    t = _grid()
    T0, beta2, gamma = 1.0, -1.0, 1.0
    P0 = fundamental_soliton_power(T0, beta2, gamma)
    assert abs(soliton_order(P0, T0, beta2, gamma) - 1.0) < 1e-9
    A0 = sech_pulse(t, T0=T0, P0=P0)
    z0 = (np.pi / 2) * dispersion_length(T0, beta2)   # one soliton period
    A = split_step_fourier(A0, t, z0, 4000, beta2=beta2, gamma=gamma)
    assert abs(np.max(np.abs(A)) - np.max(np.abs(A0))) / np.max(np.abs(A0)) < 2e-3
    assert abs(rms_width(A, t) - rms_width(A0, t)) / rms_width(A0, t) < 2e-3


def test_sw_p3_energy_conservation():       # SW-P3
    t = _grid()
    A0 = gaussian_pulse(t, T0=1.0)
    A = split_step_fourier(A0, t, 5.0, 1000, beta2=-1.0, gamma=1.0)
    assert abs(energy(A, t) - energy(A0, t)) / energy(A0, t) < 1e-6


def test_sw_p4_loss_decay():                # SW-P4
    t = _grid()
    A0 = gaussian_pulse(t, T0=1.0)
    alpha, z = 0.2, 3.0
    A = split_step_fourier(A0, t, z, 1000, beta2=-1.0, alpha=alpha)
    assert abs(energy(A, t) / energy(A0, t) - np.exp(-alpha * z)) < 1e-4


def test_sw_p5_spm_phase_only():            # SW-P5
    t = _grid()
    A0 = gaussian_pulse(t, T0=1.0, P0=2.0)
    A = split_step_fourier(A0, t, 2.0, 1000, beta2=0.0, gamma=1.0)
    assert np.allclose(np.abs(A) ** 2, np.abs(A0) ** 2, atol=1e-6)
