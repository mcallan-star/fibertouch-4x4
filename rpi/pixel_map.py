"""Map a camera frame -> 4x4 receiver brightness via 16 fixed ROIs (row-major)."""
import numpy as np

GRID = 4


class ReceiverMap:
    def __init__(self, rois):
        # rois: list of 16 (y0, x0, y1, x1) boxes, row-major
        if len(rois) != GRID * GRID:
            raise ValueError("need 16 ROIs")
        self.rois = rois

    @classmethod
    def regular_grid(cls, x0, y0, dx, dy, box):
        rois = []
        for r in range(GRID):
            for c in range(GRID):
                cx = x0 + c * dx
                cy = y0 + r * dy
                rois.append((cy - box // 2, cx - box // 2,
                             cy + box // 2, cx + box // 2))
        return cls(rois)

    def read(self, frame):
        frame = np.asarray(frame, dtype=float)
        out = np.zeros((GRID, GRID), dtype=float)
        for idx, (y0, x0, y1, x1) in enumerate(self.rois):
            patch = frame[max(0, y0):y1, max(0, x0):x1]
            out[idx // GRID, idx % GRID] = patch.mean() if patch.size else 0.0
        return out
