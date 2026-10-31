# Phase 0 Research: Pure Physics Engine Module & Test Suite

**Feature**: `002-solar-core-physics`
**Date**: 2026-10-29

## Research Topics & Decisions

### 1. Solar Position Calculation Architecture

- **Decision**: Use `pvlib.solarposition.get_solarposition` with explicit timezone verification and normalization to UTC.
- **Rationale**:
  - `pvlib` is the recognized scientific standard for PV modeling.
  - Raising a `ValueError` for timezone-naive timestamps prevents silent timezone offset bugs (critical for Alice Springs with its fractional UTC+09:30 offset).
  - Normalizing any timezone-aware index to UTC ensures deterministic, pure functional execution across all monorepo modules.
- **Alternatives Considered**:
  - *Custom astronomical equations (e.g. NOAA Solar Calculator formulas)*: High maintenance burden and potential discrepancies with industry standard validation benches. `pvlib` is already a pinned project dependency.
  - *Silently assuming local time or UTC for naive indices*: Rejected per Constitution Principle III (Fractional timezone resampling rule) and clean code reliability.

---

### 2. Clear-Sky Irradiance Transposition Model

- **Decision**: Combine `pvlib.location.Location.get_clearsky(model='ineichen')` with `pvlib.irradiance.get_total_irradiance(model='isotropic')`.
- **Rationale**:
  - The Ineichen model is robust, accounts for site altitude (545.0m elevation in Alice Springs), and uses standard Linke turbidity without external API calls.
  - `get_total_irradiance` accurately transposes direct, diffuse, and ground-reflected components to the 20° tilt and 0° North azimuth plane.
  - All values where solar zenith $\ge 90.0^\circ$ or irradiance $< 0.0$ are hard-clamped to $0.0$ $W/m^2$ to eliminate twilight artifacts.
- **Alternatives Considered**:
  - *Haurwitz clear sky model*: Simpler, but does not distinguish direct and diffuse irradiance, reducing transposition accuracy on tilted arrays.
  - *Perez transposition model*: Requires empirical atmospheric coefficients that introduce unnecessary variance without measured DNI/DHI separation.

---

### 3. Clear-Sky Power Derating & Calibration

- **Decision**: Model DC capacity scaling ($P_{dc} = G_{poa} / 1000 \times 5.4\text{ kWp}$), empirical calibration ($0.92$), linear thermal derating ($\eta_{thermal} = 1.0 + \gamma \cdot (T_{cell} - 25)$ with $\gamma = -0.004 / ^\circ\text{C}$), and inverter clipping ceiling ($5.0\text{ kW}$).
- **Rationale**:
  - Matches DKASC Site 14 specifications and audited empirical constants in `solar-physics-guard`.
  - The empirical calibration factor ($0.92$) accounts for real-world optical soiling, wiring losses, and module tolerance audited on the clearest days.
  - Linear cell temperature derating guarantees physical monotonicity (MR2 and MR3).
  - Enforces inverter AC ceiling ($5.0\text{ kW}$) to reflect physical hardware saturation.
- **Alternatives Considered**:
  - *Detailed single-diode (De Soto) model*: Requires 5 module parameters ($I_L, I_0, R_s, R_{sh}, a$) not provided in standard DKASC public plant metadata. Linear derating with empirical calibration matches real plant audit observations with $< 1\%$ discrepancy on clear days.

---

### 4. Engineering Decision #1 Nighttime Clamping (`is_night`)

- **Decision**: Define `is_night(clear_sky_power_kw: pd.Series, threshold_kw: float = 0.1) -> pd.Series` where $P < \text{threshold\_kw}$ is marked `True`.
- **Rationale**:
  - Real-world telemetry exhibits sensor noise and zero-division instability near sunrise and sunset when clear-sky power is under 100W ($0.1\text{ kW}$).
  - Enforces Engineering Decision #1 from the data audit, providing a consistent boolean mask for data filtering, loss calculation, and metamorphic testing (MR1/MR4).
- **Alternatives Considered**:
  - *Solar zenith threshold alone (zenith > 90°)*: Solar geometry alone does not account for horizon obstructions and low-light inverter start-up thresholds (typically 50–100W). Using clear-sky power $< 0.1$ kW provides both geometric and electrical stability.

---

### 5. Alice Springs Solstice Astronomical Ground Truths

- **Decision**: Encode exact solstice physical checks in golden tests for DKASC Site 14 (Lat -23.7618°, Lon 133.8748°):
  - **June 21 (Winter Solstice)**:
    - Day length: $10.3 \pm 0.5$ hours.
    - Solar noon zenith: $\approx 47.3^\circ$ (peak elevation $\approx 42.7^\circ$).
    - Clear-sky power peak: Lower diurnal amplitude ($\approx 3.2 - 3.8\text{ kW}$).
  - **December 21 (Summer Solstice)**:
    - Day length: $13.7 \pm 0.5$ hours.
    - Solar noon zenith: $< 1.0^\circ$ (peak elevation $\approx 89.6^\circ$, sun directly overhead near Tropic of Capricorn).
    - Clear-sky power peak: High diurnal amplitude, reaching inverter clipping saturation ($5.0\text{ kW}$).
- **Rationale**:
  - Provides deterministic, astronomical golden standards verifying that site coordinates, tilt, azimuth, and hemisphere conventions are flawlessly configured.
