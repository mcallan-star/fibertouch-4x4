# FiberTouch 4x4 - Test & Verification Plan

**Project:** FiberTouch 4x4 - Fiber-Optic Touch Sensing & Signal-Propagation Model **Document type:** Test plan / verification plan **Status:** Living document (update as stages complete) **Owner:** Madeleine Callan

---

## 1. Purpose of this document

This plan defines *how we prove that FiberTouch works* - and, just as importantly, *how we measure and characterize it* when it doesn't. It is written the way an optics/hardware integration team would qualify a new component: bottom-up, one isolated effect at a time, with explicit pass/fail criteria, a link budget, a crosstalk budget, and a failure-analysis path for every known risk.

It covers four verification levels:

1. **Software / algorithm tests** - the signal-processing and optical-model code, run automatically.
2. **Optical bench characterization** - per-pixel insertion loss, reflected-signal contrast, and crosstalk.
3. **Staged hardware bring-up** - one pixel -> 2x2 -> full 4x4, each with entry/exit criteria.
4. **System acceptance** - the end-to-end live touch map against the project's success criteria.

---

## 2. What the project is (walkthrough)

FiberTouch 4x4 is a **proof-of-concept remote optical touch surface**. The touch panel itself contains *no electronics* - light is carried to and from the surface through optical fibers, and all active parts (LEDs, camera, controller) live in a separate enclosure.

**Physical layout.** A 4x4 grid of sixteen *pixels*. Each pixel is a pair of fibers mounted flush with the front plate:

- **TX fiber** - carries 850 nm infrared light from an LED up to the surface.
- **RX fiber** - collects light scattered back when a finger covers the pixel and carries it to a second 4x4 grid that a camera images.

```
 Infrared LED ──▶ TX fiber ──▶ touch surface ──(finger scatters light)──▶ RX fiber ──▶ camera receiver grid
```

**Sensing principle.** With no finger present, little TX light reaches the RX fiber. A finger reflects/scatters extra IR into the RX fiber, so the camera sees that receiver spot get brighter. Touch is decided from the *change versus an untouched baseline*.

**Signal chain.** The controller scans **one pixel at a time** so it always knows which transmitter produced the reflected light:

```
1. all LEDs off -> capture ambient frame
2. LED[i] on    -> capture frame, measure brightness at receiver[i]
3. LED[i] off   -> repeat for i = 1..16
4. compare every reading to its stored untouched baseline
5. mark pixels whose change exceeds a calibrated threshold -> render touch map
```

**Two engineering halves (and why both are tested).**

| Half | What it is | Where it lives |
|------|-----------|----------------|
| Sensing pipeline | Camera readout: ambient subtraction, per-pixel baseline calibration, normalization, thresholding -> live touch map | `touch_sensing.py` |
| Optical signal model | Link/crosstalk budget (dB losses through TX->surface->RX) + a split-step Fourier NLSE solver for IR propagation in the fibers; used to predict received signal and set thresholds | `touch_sensing.py`, `fiber_propagation.py` |

The model exists so that thresholds, pixel pitch, and expected contrast are *derived from optics*, not guessed - and so a failing pixel can be diagnosed as a coupling-loss problem, a crosstalk problem, or a leakage problem rather than just "it doesn't work."

---

## 3. System under test

| Subsystem | Items |
|-----------|-------|
| Controller | Raspberry Pi (Raspberry Pi OS), Python software |
| IR illumination | 16x 850 nm IR LEDs, current-limiting resistors, PCA9685 16-channel PWM driver, regulated supply |
| Optical | 16 TX + 16 RX fibers (1 mm, 850 nm-rated or end-glow POF), black heat-shrink LED couplings, opaque housings |
| Camera | Raspberry Pi Camera Module NoIR (IR-sensitive) |
| Mechanical | Black front plate, LED coupling plate, camera receiver plate, opaque pixel grid, enclosure |

**Nominal geometry:** fiber Ø 1 mm; TX-RX spacing 1.5-2 mm; pixel pitch 8-10 mm; plate thickness 3-5 mm; array 35-45 mm square.

---

## 4. Definitions & measured metrics

All optical readings are camera brightness values for a receiver spot unless noted.

| Symbol / term | Definition | Why it matters |
|---------------|------------|----------------|
| `ambient[i]` | brightness at receiver *i* with all LEDs off | removes room light |
| `illum[i]` | brightness at receiver *i* with LED *i* on | raw signal |
| `signal[i]` | `illum[i] - ambient[i]` | ambient-subtracted signal |
| `baseline[i]` | averaged `signal[i]` with no finger (untouched) | reference state |
| `touch_change[i]` | `signal[i] - baseline[i]` | the quantity thresholded |
| **Contrast** | `touch_change_touched / baseline` (per pixel) | touched-vs-untouched separation; analogous to a detection margin |
| **Noise σ** | std. dev. of `touch_change` over N untouched frames | sets the threshold floor |
| **SNR** | `touch_change_touched / σ` | detection confidence (target ≥ 5) |
| **Insertion loss** | per-pixel optical loss TX->surface->RX, in dB | identifies weak fibers/couplings |
| **Crosstalk / isolation** | neighbor `touch_change` ÷ touched-pixel `touch_change`, in dB | prevents false neighbor triggers |
| **Refresh rate** | full 16-pixel scans per second (Hz) | interactivity |

**Link-budget relation (modeled in `received_power_dbm`):**

```
P_rx(dBm) = P_led - 2, (coupling loss) - 2, (fiber attenuation x length) - (finger reflection loss)
```

A pixel is **detectable** when its touched contrast clears the noise floor with the target SNR margin.

---

## 5. Test strategy

- **Bottom-up & risk-first.** Verify the algorithm in software, then one optical pixel, then interactions (crosstalk) at 2x2, then the full array. Each known risk (Section 10) has a dedicated check.
- **Characterize, don't just pass/fail.** Every optical test records a *number* (dB, SNR, Hz), so marginal pixels are visible before they fail.
- **One variable at a time.** Hardware changes (spacing, LED current, exposure) are swept individually and logged.
- **Regression-protected.** The software pipeline has an automated test suite that must stay green before any hardware data is trusted.

**Entry criterion for each stage:** the previous stage met its exit criteria. **Exit criterion:** all "must" rows in that stage's table pass and data is logged.

---

## 6. Level 1 - Software / algorithm tests (automated)

These run with no hardware and lock down the math before any optical data is interpreted. They are executed with:

```bash
pip install numpy pytest
pytest -v        # expected: all green
```

### 6.1 Optical-model tests (`touch_sensing.py`)

| ID | Test | Method | Pass criterion |
|----|------|--------|----------------|
| SW-O1 | dB ↔ linear conversion | round-trip `db_to_linear`/`linear_to_db` | matches to 1e-9 |
| SW-O2 | Link budget | `received_power_dbm` vs hand-computed dB sum | equal (e.g. 7.4 dB loss -> -7.4 dBm) |
| SW-O3 | Length dependence | longer fiber | received power strictly decreases |
| SW-O4 | Crosstalk model | `crosstalk_ratio` vs pixel pitch | falls with pitch, stays in (0,1) |
| SW-O5 | Input guarding | invalid pitch/length | raises `ValueError` |

### 6.2 Sensing-pipeline tests (`touch_sensing.py`)

| ID | Test | Method | Pass criterion |
|----|------|--------|----------------|
| SW-S1 | Ambient subtraction | `signal()` on synthetic frames | `illum - ambient` exactly |
| SW-S2 | Baseline calibration | average N untouched frames | baseline = mean signal |
| SW-S3 | Known touch pattern | synthetic frame, fingers on (0,2),(1,1) | touch map equals expected boolean grid |
| SW-S4 | Threshold discrimination | change below threshold | not flagged |
| SW-S5 | Calibration guard | detect before calibrate | raises `RuntimeError` |
| SW-S6 | Frame-shape guard | non-4x4 frame | raises `ValueError` |
| SW-S7 | Map rendering | `render_map` | `". . X ."` formatting correct |

### 6.3 Propagation-solver tests (`fiber_propagation.py`)

| ID | Test | Method | Pass criterion |
|----|------|--------|----------------|
| SW-P1 | Dispersive broadening | Gaussian under pure GVD | RMS width grows by √(1+(z/L_D)^2) |
| SW-P2 | Soliton invariance | N=1 sech pulse over one period | peak power & width unchanged (≤ 0.2%) |
| SW-P3 | Energy conservation | lossless run | energy constant (Parseval) |
| SW-P4 | Loss | α > 0 | energy decays as exp(-αz) |
| SW-P5 | SPM only | β₂ = 0 | temporal intensity unchanged |

**Exit criteria (Level 1):** 100% of SW-* tests pass in CI on every commit.

---

## 7. Level 2 - Optical bench characterization (per pixel)

Performed in the dark receiver enclosure, fibers mounted, camera fixed.

### 7.1 Per-pixel insertion-loss / signal survey

**Procedure**

1. All LEDs off; capture ambient. Record `ambient[i]`.
2. For each pixel *i*: LED *i* on at the nominal PWM level; capture; record `illum[i]`; LED off.
3. Compute `signal[i] = illum[i] - ambient[i]` and convert relative levels to dB against the array median.

**Pass criteria**

| Check | Target |
|-------|--------|
| All 16 receivers visible & uniquely located in camera image | must |
| Per-pixel signal within band of median | ≤ 6 dB spread (else flag for re-polish / re-align) |
| No receiver saturated or clipped | must (adjust exposure) |

### 7.2 Touched-vs-untouched contrast & SNR

**Procedure**

1. Calibrate baseline: N ≥ 20 untouched frames -> `baseline[i]`, noise `σ[i]`.
2. Place a finger over pixel *i*; capture; compute `touch_change[i]`.
3. Repeat for all pixels; compute contrast and SNR.

**Pass criteria**

| Check | Target |
|-------|--------|
| Touched `touch_change` positive & repeatable | must |
| SNR = touch_change / σ | ≥ 5 (≥ 3 marginal-pass, flag) |
| Contrast (touched ÷ baseline) | ≥ 0.5 (tune LED current / spacing if below) |

### 7.3 Crosstalk / optical isolation

**Procedure**

1. Touch pixel *i*. Record `touch_change` at *i* and at its 4-neighbors.
2. Isolation(dB) = 10, log₁₀(neighbor change ÷ touched change).

**Pass criteria**

| Check | Target |
|-------|--------|
| Neighbor isolation | ≥ 6 dB (neighbor change < 25% of touched) |
| No neighbor crosses its own touch threshold | must |

> Ties to model: compare measured isolation to `crosstalk_ratio(pitch, isolation_len)`.
> If measured crosstalk is worse than predicted, the opaque pixel grid or fiber
> separation is the suspect (Section 10, Light leakage).

---

## 8. Level 3 - Staged hardware bring-up

### Stage 1 - One pixel
**Build:** 1 TX + 1 RX pair. **Goal:** prove a finger produces a measurable, repeatable camera change.

| Test | Pass criterion |
|------|----------------|
| Camera sees the RX spot | must |
| Finger on -> measurable `touch_change` | SNR ≥ 5 over 10 touch/release cycles |
| Repeatability | touched and untouched ranges do not overlap |
| (Risk check) IR transmission adequate at 850 nm | if weak, follow Insufficient-IR mitigations (Section 10) |

**Exit:** stable, separable touched/untouched signal on one pixel.

### Stage 2 - 2x2 (four pixels)
**Build:** 4 pixels; first use of multiplexed LED control + camera-region mapping.

| Test | Pass criterion |
|------|----------------|
| Each LED independently addressable via PCA9685 | all 4 toggle correctly |
| Camera region -> pixel index mapping | each receiver maps to exactly one pixel |
| Neighbor crosstalk (Section 7.3) | ≥ 6 dB isolation on all adjacent pairs |
| Scan sequence correctness | touched pixel == illuminated pixel, no aliasing |

**Exit:** four pixels resolve independently with acceptable isolation.

### Stage 3 - Full 4x4
**Build:** all 16 pixels.

| Test | Pass criterion |
|------|----------------|
| All 16 transmitters independently controllable | must |
| All 16 receivers visible & mapped | must |
| Live touch map | renders correctly for single touches |
| Calibration & per-pixel thresholds | stored; survive recalibration |
| Scan speed | meets refresh target (Section 9) |

**Exit:** full-array system meets the acceptance criteria in Section 9.

### Stage 4+ (out of scope for this plan)
Visible-fiber/RGB display integration and 8x8 / 32x32 scale-up - to be covered by a follow-on plan.

---

## 9. Level 4 - System acceptance criteria

Maps directly to the project's stated success criteria.

| ID | Acceptance test | Target |
|----|-----------------|--------|
| AC-1 | Single-pixel identification accuracy | correctly identifies ≥ **14 of 16** pixels |
| AC-2 | Independent transmitter control | all 16 controllable |
| AC-3 | Receiver visibility | all 16 visible to camera |
| AC-4 | Repeatable measurable change on touch | every pixel, across trials |
| AC-5 | Neighbor false-trigger rate | neighbors do **not** regularly trigger (≥ 6 dB isolation) |
| AC-6 | Refresh rate | ≥ **3-5 full scans/sec** (feels interactive) |
| AC-7 | Stability after recalibration | results consistent across recalibration cycles |
| AC-8 | Ambient robustness | operates under normal indoor lighting after calibration |

**Known non-goals (not tested / expected to fail):** precise pressure, exact fingertip shape, dense multi-touch, direct-sunlight operation, smartphone-grade sensitivity.

---

## 10. Failure analysis & risk-based tests

For each known risk: the symptom, the diagnostic, and the mitigation to re-test.

| Risk | Symptom in data | Diagnostic test | Mitigation -> re-test |
|------|-----------------|-----------------|----------------------|
| **Insufficient IR transmission** | low `signal[i]` across the board | single-pair Stage-1 power check; swap to 850 nm-rated fiber or visible red for debug | shorten fibers, rated fiber, raise LED current within limits -> re-run 7.1 |
| **Weak reflected signal** | low SNR / contrast on touch | sweep TX-RX spacing & LED current; add thin contact layer; raise exposure; average more frames | re-run 7.2 until SNR ≥ 5 |
| **Light leakage** | high baseline, neighbors near threshold, poor isolation | dark-chamber test; LED-on with RX path blocked should read ≈ ambient | opaque housings, heat-shrink couplings, separate bundles -> re-run 7.3 |
| **Uneven fibers** | > 6 dB pixel-to-pixel spread | per-pixel insertion-loss survey (7.1) | polish ends, avoid sharp bends, per-pixel calibration & thresholds -> re-run 7.1 |
| **Ambient interference** | drift with room light | toggle room lights during a scan | confirm ambient-frame subtraction; enclose receiver |

---

## 11. Calibration verification

The system is only valid against a current calibration.

1. Front surface uncovered; capture N ≥ 20 frames per pixel.
2. Average -> `baseline[i]`; record noise `σ[i]`.
3. Touch each pixel; record typical touched levels.
4. Set per-pixel threshold between untouched and touched ranges (≥ 5σ above baseline recommended).
5. Store per-pixel thresholds (couplings differ, so global thresholds are insufficient).

**Verification:** AC-7 (re-run calibration twice; thresholds and the resulting touch map for a fixed finger pattern must agree).

---

## 12. Traceability matrix (objective -> test)

| Objective / success criterion | Verified by |
|-------------------------------|-------------|
| Detect which of 16 areas is touched | AC-1, Stage 3 |
| Prevent neighbor interference | 7.3, Stage 2, AC-5 |
| Approximate touch strength / contact quality | 7.2 (contrast/SNR) |
| Per-pixel uniformity | 7.1, calibration §11 |
| Interactive refresh | AC-6 |
| Stable after recalibration | §11, AC-7 |
| Operates in indoor light | AC-8 |
| Correct signal math | SW-S*, SW-O* |
| Optical propagation model valid | SW-P* |

---

## 13. Test environment, equipment & data logging

- **Software:** Python 3, NumPy, pytest; CI runs the Level-1 suite on every commit.
- **Hardware bench:** dark receiver enclosure, fixed camera mount, regulated supply, PCA9685, multimeter, (optional) optical power meter for absolute insertion-loss.
- **Data logging:** for every optical test, log per-pixel `ambient`, `illum`, `signal`, `baseline`, `σ`, `touch_change`, contrast, SNR, isolation, exposure/LED settings, and a timestamp. Store raw camera frames for any failed pixel for failure analysis.

**Touch-map log format**

```
. . X .
. X . .
. . . .
. . . .   (X = touched, . = untouched)
```

---

## 14. Exit / sign-off

The prototype is accepted when **all Level-1 software tests pass**, **Stages 1-3 exit criteria are met**, and **all AC-* acceptance criteria pass**, with the characterization data (insertion loss, SNR, crosstalk) logged for every pixel.

| Level | Status | Date | Notes |
|-------|--------|------|-------|
| L1 - Software suite | ☐ | | |
| L2 - Optical characterization | ☐ | | |
| L3 - Stage 1 / 2 / 3 | ☐ / ☐ / ☐ | | |
| L4 - System acceptance | ☐ | | |
