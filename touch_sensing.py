"""FiberTouch 4x4 - sensing pipeline + optical link/crosstalk model.

Camera-side touch detection (ambient subtraction, baseline calibration,
thresholding) plus the simple dB link budget and crosstalk model used to
pick thresholds and pixel pitch.
"""
import numpy as np

GRID = 4


# --------------------------------------------------------------------------
# optical model
# --------------------------------------------------------------------------
def db_to_linear(db):
    """dB -> linear power ratio."""
    return 10.0 ** (np.asarray(db, dtype=float) / 10.0)


def linear_to_db(ratio):
    """linear power ratio -> dB."""
    ratio = np.asarray(ratio, dtype=float)
    if np.any(ratio <= 0):
        raise ValueError("ratio must be positive")
    return 10.0 * np.log10(ratio)


def received_power_dbm(p_led_dbm, coupling_loss_db, fiber_atten_db_per_m,
                       length_m, finger_reflection_loss_db):
    """Link budget for one pixel, TX -> surface -> RX.

    P_rx = P_led - 2*coupling - 2*(atten*length) - finger_reflection
    The factor of 2 covers both the TX and RX legs.
    """
    if length_m < 0:
        raise ValueError("length_m must be >= 0")
    if fiber_atten_db_per_m < 0 or coupling_loss_db < 0:
        raise ValueError("losses must be >= 0")
    return (float(p_led_dbm)
            - 2.0 * float(coupling_loss_db)
            - 2.0 * float(fiber_atten_db_per_m) * float(length_m)
            - float(finger_reflection_loss_db))


def crosstalk_ratio(pitch_mm, isolation_len_mm):
    """Linear crosstalk ratio (neighbour / touched) in (0, 1).

    Exponential isolation: tighter pitch -> more leak, bigger isolation
    length (better separation) -> less leak.
    """
    if pitch_mm <= 0 or isolation_len_mm <= 0:
        raise ValueError("pitch and isolation length must be > 0")
    return float(np.exp(-float(pitch_mm) / float(isolation_len_mm)))


# --------------------------------------------------------------------------
# sensing pipeline
# --------------------------------------------------------------------------
class TouchPanel:
    """4x4 touch decision from camera receiver-grid brightness."""

    def __init__(self, grid=GRID, threshold=10.0):
        self.grid = grid
        self.threshold = float(threshold)
        self.baseline = None
        self.noise = None

    def _check(self, frame):
        frame = np.asarray(frame, dtype=float)
        if frame.shape != (self.grid, self.grid):
            raise ValueError(
                "frame must be %dx%d, got %r" % (self.grid, self.grid, frame.shape))
        return frame

    def signal(self, illum, ambient):
        """Ambient-subtracted signal."""
        return self._check(illum) - self._check(ambient)

    def calibrate(self, frames):
        """Average untouched (illum, ambient) frames -> baseline + noise sigma."""
        sigs = [self.signal(i, a) for (i, a) in frames]
        if not sigs:
            raise ValueError("need at least one calibration frame")
        stack = np.stack(sigs, axis=0)
        self.baseline = stack.mean(axis=0)
        self.noise = stack.std(axis=0)
        return self.baseline

    def touch_change(self, illum, ambient):
        """signal - baseline."""
        if self.baseline is None:
            raise RuntimeError("calibrate() before detecting")
        return self.signal(illum, ambient) - self.baseline

    def normalized_signal(self, illum, ambient):
        """touch_change / baseline (per-pixel contrast). Guards div-by-zero."""
        if self.baseline is None:
            raise RuntimeError("calibrate() before detecting")
        base = np.where(np.abs(self.baseline) < 1e-9, 1e-9, self.baseline)
        return self.touch_change(illum, ambient) / base

    def touch_map(self, illum, ambient, threshold=None):
        """Boolean 4x4 of touched pixels."""
        thr = self.threshold if threshold is None else float(threshold)
        return self.touch_change(illum, ambient) > thr


def render_map(boolmap):
    """Boolean grid -> '. . X .' style text."""
    boolmap = np.asarray(boolmap)
    rows = []
    for r in boolmap:
        rows.append(" ".join("X" if v else "." for v in r))
    return "\n".join(rows)
