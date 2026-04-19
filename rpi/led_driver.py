"""16x 850nm IR LEDs over a PCA9685 16-ch PWM driver (I2C).

needs: adafruit-circuitpython-pca9685, adafruit-blinka
pixel i -> channel i, row i//4, col i%4.
"""
try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
except ImportError:  # so it imports off-Pi for docs/tests
    board = busio = PCA9685 = None

GRID = 4
N = GRID * GRID


class LEDArray:
    def __init__(self, frequency=1000, address=0x40):
        if PCA9685 is None:
            raise RuntimeError("adafruit PCA9685 libs not available (run on a Pi)")
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(i2c, address=address)
        self.pca.frequency = frequency

    def set_brightness(self, i, level):
        # level 0..1 -> 16-bit duty
        level = max(0.0, min(1.0, float(level)))
        self.pca.channels[i].duty_cycle = int(level * 0xFFFF)

    def on(self, i, level=1.0):
        self.set_brightness(i, level)

    def off(self, i):
        self.pca.channels[i].duty_cycle = 0

    def all_off(self):
        for i in range(N):
            self.pca.channels[i].duty_cycle = 0

    def deinit(self):
        self.all_off()
        self.pca.deinit()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.deinit()
