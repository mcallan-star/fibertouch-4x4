"""FiberTouch 4x4 - sensing pipeline (camera side). wip."""
import numpy as np

GRID = 4


class TouchPanel:
    def __init__(self, grid=GRID, threshold=10.0):
        self.grid = grid
        self.threshold = float(threshold)
        self.baseline = None

    def signal(self, illum, ambient):
        return np.asarray(illum, float) - np.asarray(ambient, float)

    def calibrate(self, frames):
        sigs = [self.signal(i, a) for (i, a) in frames]
        self.baseline = np.mean(sigs, axis=0)
        return self.baseline

    def touch_change(self, illum, ambient):
        return self.signal(illum, ambient) - self.baseline

    def touch_map(self, illum, ambient, threshold=None):
        thr = self.threshold if threshold is None else float(threshold)
        return self.touch_change(illum, ambient) > thr


def render_map(boolmap):
    return "\n".join(" ".join("X" if v else "." for v in r)
                      for r in np.asarray(boolmap))
