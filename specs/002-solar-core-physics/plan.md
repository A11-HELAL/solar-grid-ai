# Implementation Plan: Pure Physics Engine Module & Test Suite

**Branch**: `002-solar-core-physics` | **Date**: 2026-10-29 (Updated: 2026-11-18) | **Spec**: [specs/002-solar-core-physics/spec.md](spec.md)

**Input**: Feature specification from `specs/002-solar-core-physics/spec.md`

## Summary

Build the pure domain physics engine `packages/solar_core/physics.py` and its comprehensive test suite `tests/test_physics.py`. Implements pure functions `calculate_solar_position`, `calculate_clear_sky_poa`, `calculate_faiman_cell_temperature`, `calculate_clear_sky_power`, and `is_night`, enforcing UTC timestamp awareness, Ineichen clear-sky modeling transposed to DKASC Site 14 geometry (20° tilt, 0° North azimuth), Faiman empirical module temperature modeling, empirical calibration (0.92), cell temperature derating ($\gamma = -0.004 / ^\circ\text{C}$), inverter clipping (`config.inverter_ac_cap_kw` = 5.0 kW), and Engineering Decision #1 night masking (`config.night_threshold_kw` = 0.1 kW or solar zenith $\ge 90^\circ$). Validates MR4 metamorphic property tests and Alice Springs June/December Solstice golden curves with zero external I/O or system clock dependencies.

## Technical Context

**Language/Version**: Python 3.10+ (Standard Library `typing`, `zoneinfo`)

**Primary Dependencies**: `pvlib>=0.10.0`, `pandas>=2.0.0`, `numpy>=1.24.0`, `solar_core.config` (`PlantConfig`)

**Storage**: In-memory Series and DataFrames; zero database, filesystem, or disk caching in `packages/solar_core/physics.py`

**Testing**: `pytest>=7.0.0` (Comprehensive property and golden test suite in `tests/test_physics.py`)

**Target Platform**: Windows 10 / Linux host

**Project Type**: Monorepo pure core domain library (`packages/solar_core`)

**Performance Goals**: Hourly full-year computation (8,760 timestamps) in $< 250\text{ms}$; single timestamp calculations in $< 50\mu\text{s}$

**Constraints**: Strict single-threaded sequential execution; no multiprocessing pools; 100% pure functions (no DB, no network, no `now()`, no `pickle`); strict type annotations

**Scale/Scope**: 1 domain physics module (`packages/solar_core/physics.py`), 1 package initializer update (`packages/solar_core/__init__.py`), 1 comprehensive test file (`tests/test_physics.py`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitutional Invariant | Status | Verification Detail |
|---|---|---|
| **Principle I: Strict Sequential Execution & Resource Governance** | **PASS** | Physics calculations execute single-threaded on vectorized NumPy/pandas arrays without parallel multiprocessing pools or worker queues. |
| **Principle II: Canonical Monorepo & Pure Functional Core** | **PASS** | Implements step 2 of `solar_core` build order (`config.py` → `physics.py`). 100% pure functions located in `packages/solar_core/`: zero database queries, zero socket calls, zero `datetime.now()`, zero `pickle`. |
| **Principle III: Mandatory 7 Engineering Decisions** | **PASS** | Enforces Decision #1 (`is_night` at `clear_sky_kw < 0.1` or zenith $\ge 90^\circ$), Decision #3 Faiman module temperature modeling (`pvlib.temperature.faiman`), DKASC Site 14 constants (`inverter_ac_cap_kw` = 5.0 kW), and explicit UTC timestamp conversions. |
| **Principle IV: Metamorphic Testing & Strict Physics QA Gates** | **PASS** | Implements property tests directly validating MR4 (night power identically 0.0 kW regardless of temperature/weather inputs) and solstice physical bounds. |
| **Principle V: Tiered Delegation & Multi-Guard Verification** | **PASS** | High-level planning authored by architect; code and pytest tasks ready for sequential delegate execution and guard audits. |

*Post-Design Evaluation*: All gates confirmed passing. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/002-solar-core-physics/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Phase 0 output (transposition models, derating, solstice checks)
├── data-model.md        # Phase 1 output (data structures, physics invariants)
├── quickstart.md        # Phase 1 output (runnable validation & quickstart guide)
├── contracts/           # Phase 1 output
│   └── physics-api.md   # Module interface contract for packages/solar_core/physics.py
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks output)
```

### Source Code (repository root)

```text
packages/solar_core/
├── __init__.py          # Updated to export calculate_solar_position, calculate_clear_sky_poa, calculate_faiman_cell_temperature, calculate_clear_sky_power, is_night
├── config.py            # Existing PlantConfig (with inverter_ac_cap_kw, night_threshold_kw)
└── physics.py           # Pure physics functions (solar position, clear-sky POA, Faiman cell temp, power, is_night, thin backward-compat aliases)

tests/
├── __init__.py
├── test_config.py       # Config tests (canonical flat path)
└── test_physics.py      # Comprehensive unit, property (MR4), and golden solstice tests
```

**Structure Decision**: Builds step 2 of the pure core architecture in `packages/solar_core/physics.py`, with unit and metamorphic tests placed in `tests/test_physics.py` directly testable via standard `pytest`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No constitutional violations. Zero complexity justification required.*
