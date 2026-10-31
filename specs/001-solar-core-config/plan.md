# Implementation Plan: Foundational Solar Core Configuration & Packaging

**Branch**: `001-solar-core-config` | **Date**: 2026-10-26 | **Spec**: [specs/001-solar-core-config/spec.md](spec.md)

**Input**: Feature specification from `specs/001-solar-core-config/spec.md`

## Summary

Build the foundational, pure domain configuration module `solar_core/config.py`, package entrypoint `solar_core/__init__.py` (exposing `CORE_VERSION = "1.1.0"`), standard `pyproject.toml` (for editable install `pip install -e .`), and root `plant_config.yaml` for DKASC Site 14 (`dka_01`). All configuration entities use standard library `@dataclass(frozen=True, slots=True)` enforcing physical realism bounds, runtime immutability, canonical quality flags, cryptographic raw data hashing, and ML feature column contracts with zero external runtime service dependencies.

## Technical Context

**Language/Version**: Python 3.10+ (Standard Library `dataclasses`, `zoneinfo`, `pathlib`, `typing`)

**Primary Dependencies**: `pyyaml>=6.0`, `pvlib>=0.10.0`, `numpy>=1.24.0`, `pandas>=2.0.0`, `pydantic>=2.0.0`, `tzdata` (Windows timezone support), `setuptools>=61.0` (build backend)

**Storage**: Local filesystem configuration (`plant_config.yaml`), serialized models/metadata in future phases; zero database access in `solar_core`

**Testing**: `pytest>=7.0.0`, `pytest-cov>=4.0.0` (Unit tests located in `tests/unit/test_config.py`)

**Target Platform**: Windows 10 / Linux local host (Intel Core i5-7200U, 8GB RAM, 1TB mechanical HDD)

**Project Type**: Monorepo pure core domain library (`solar_core`) with editable root installation

**Performance Goals**: Configuration load & validation $< 10\text{ms}$; instantiation overhead $< 1\mu\text{s}$ per dataclass; zero memory leaks via `slots=True`

**Constraints**: Strict single-threaded sequential execution; no raw CSV ingestion into LLM context; zero DB/network/`now()`/`pickle` in `solar_core`; strict immutability

**Scale/Scope**: 1 package initializer, 1 configuration module, 1 project packaging manifest, 1 root YAML config, 1 comprehensive unit test suite

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitutional Invariant | Status | Verification Detail |
|---|---|---|
| **Principle I: Strict Sequential Execution & Resource Governance** | **PASS** | Implementation and test runs are strictly single-threaded; no parallel worktrees or background subprocesses spawned. No raw CSV data accessed. |
| **Principle II: Canonical Monorepo & Pure Functional Core** | **PASS** | Modifies canonical directories (`solar_core/`, `tests/unit/`, root configuration). Modules follow step 1 of build order (`config.py`). 100% pure functions (no DB, no network, no `now()`, no `pickle`). |
| **Principle III: Mandatory 7 Engineering Decisions** | **PASS** | Encapsulates all DKASC Site 14 constants, 5 quality flags (`ok`, `interpolated`, `missing`, `fault_suspect`, `out_of_range`), short gap limit ($\le 2\text{h}$), inverter clipping ceiling ($4.95\text{ kW}$ in `SoilingConfig`), and night threshold ($0.1\text{ kW}$). |
| **Principle IV: Metamorphic Testing & Strict Physics QA Gates** | **PASS** | Foundation configuration defines physical constants required for MR1–MR8 boundary checks (e.g. night threshold, nameplate capacity ceiling $5.4\text{ kWp}$, thermal coefficient $\gamma = -0.004$). |
| **Principle V: Tiered Delegation & Multi-Guard Verification** | **PASS** | Specification and plan authored by architect (Gemini Pro); code and test generation delegated to execution tier; guarded by `solar-physics-guard`, `clean-code-guard`, and `test-guard`. |

*Post-Design Evaluation*: All gates confirmed passing. No violations or complexity overrides detected.

## Project Structure

### Documentation (this feature)

```text
specs/001-solar-core-config/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Phase 0 output (architectural decisions & boundaries)
├── data-model.md        # Phase 1 output (entities, fields, and invariant contracts)
├── quickstart.md        # Phase 1 output (runnable validation & quickstart guide)
├── contracts/           # Phase 1 output
│   ├── module-interface.md    # Public Python API contract
│   └── plant-config-schema.md # YAML file schema contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks output)
```

### Source Code (repository root)

```text
solar_core/
├── __init__.py          # Exposes CORE_VERSION = "1.1.0" and public configuration exports
└── config.py            # PlantConfig, SoilingConfig, ValidatorConfig, load_plant_config, contracts

plant_config.yaml        # Verified DKASC Site 14 plant configuration file
pyproject.toml           # Root build configuration for editable install (pip install -e .)

tests/
├── __init__.py
└── unit/
    ├── __init__.py
    └── test_config.py   # Comprehensive unit tests for config, validation, immutability, YAML
```

**Structure Decision**: Monorepo pure core domain library layout. `solar_core` is placed at the top level and installed in editable mode via root `pyproject.toml`. Unit tests are isolated in `tests/unit/` mirroring the domain modules.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No constitutional violations. Zero complexity justification required.*
