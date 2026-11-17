# Room 7: User Interface (`ui/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`ui` delivers the real-time operational dashboard for Solar-Grid AI, built with React 18, Vite, TypeScript, and Recharts.

### Locked Architectural Invariants
- **Contract-Bound Client**: UI data consumption maps directly to the 8 endpoints exposed by Room 6 (`docs/openapi.json`).
- **Mock-Compatible Development**: The frontend operates against either the live FastAPI backend or the deterministic mock service (`MOCK=1`), allowing UI development without local database dependencies.
- **Three Core Operational Views**:
  1. **Plant Overview**: Real-time generation, current inverter headroom (5.0 kW ceiling), solar zenith, and plant metadata.
  2. **Forecast & Health**: 24-48h day-ahead forecast vs actual generation, guardrail activation markers, daily $\text{PR}_{\text{tc}}$ trend, and estimated soiling derating curve.
  3. **Anomaly Deep Dive**: Quality flag distribution (`ok`, `interpolated`, `missing`, `fault_suspect`, `night`), inverter clipping visualization, and active system alerts.

---

## 2. Current Implementation Status

- **Setup & Tooling**: Initialized with `package.json`, TypeScript 5, Vite, React 18, and Recharts.
- **Entry Points**: `src/App.tsx` contains baseline walking skeleton rendering. Full component views scheduled for Sprint 2.
