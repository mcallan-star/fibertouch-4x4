# Stage 2 - 2x2

4 pixels, PCA9685 driving the 4 LEDs, camera ROI map per receiver.

- all 4 LEDs toggle independently, scan order == illuminated pixel. no aliasing.
- insertion loss spread ~1.1 dB across the 4, under the 6 dB flag. ok.
- adjacent isolation ~ -9 to -10 dB (neighbour change ~9% of touched). passes >=6 dB.
- one corner (1,0) slightly hotter, bumped its threshold a touch.

exit: PASS. full 4x4 (stage 3) not built yet - out of scope for now.
