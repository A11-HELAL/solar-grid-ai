# Metamorphic Relations Catalog (MR1 - MR8) - Room 8 QA Gate
Pass threshold required for model promotion to models/ACTIVE: >= 95%.

- **MR1 (Nighttime Zero Invariance)**: For any input row where zenith > 90 deg, varying ambient temp or wind speed must still yield P_pred = 0.0 kW.
- **MR2 (Irradiance Monotonicity)**: Holding temp, wind, and geometry constant during daytime (zenith < 75 deg), increasing GHI must not decrease P_pred.
- **MR3 (Thermal Derating Consistency)**: Under high irradiance (GHI > 600 W/m^2), increasing ambient temp by +10C above 25C must result in P_hot <= P_base.
- **MR4 (Physical Capacity Ceiling)**: Under extreme irradiance (GHI = 1300 W/m^2), predicted power must strictly satisfy 0.0 <= P_pred <= 5.4 kW.
- **MR5 (Cloud Opacity Damping)**: Increasing cloud cover percentage while keeping clear-sky geometry fixed must not increase P_pred.
- **MR6 (Soiling Multiplier Proportionality)**: Applying a synthetic soiling factor alpha in (0, 1) to POA irradiance must scale output downward monotonically.
- **MR7 (Temporal Lag Continuity)**: Smooth perturbations in t-1 lag power must produce bounded changes in P_pred.
- **MR8 (Clear-Sky Ratio Bounds)**: Reconstructed power P_pred = r_hat * P_clear_sky must never produce negative values or NaN.
