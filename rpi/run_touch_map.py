"""Live touch map loop. Run on the Pi after wiring + ROI calibration."""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from touch_sensing import TouchPanel, render_map   # noqa: E402
from led_driver import LEDArray                     # noqa: E402
from camera import Camera                           # noqa: E402
from pixel_map import ReceiverMap                   # noqa: E402
from scanner import Scanner                         # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x0", type=int, required=True)
    ap.add_argument("--y0", type=int, required=True)
    ap.add_argument("--dx", type=int, required=True)
    ap.add_argument("--dy", type=int, required=True)
    ap.add_argument("--box", type=int, default=12)
    ap.add_argument("--threshold", type=float, default=10.0)
    ap.add_argument("--cal-frames", type=int, default=20)
    args = ap.parse_args()

    recmap = ReceiverMap.regular_grid(args.x0, args.y0, args.dx, args.dy, args.box)
    panel = TouchPanel(threshold=args.threshold)
    with LEDArray() as leds, Camera() as cam:
        scanner = Scanner(leds, cam, recmap)
        print("calibrating baseline, keep surface clear...")
        scanner.calibrate(panel, frames=args.cal_frames)
        print("go. ctrl-c to stop.")
        try:
            while True:
                illum, ambient = scanner.scan()
                print(render_map(panel.touch_map(illum, ambient)))
                print("-" * 9)
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("bye")


if __name__ == "__main__":
    main()
