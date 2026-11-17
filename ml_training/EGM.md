# Room 3: ML Training & Model Zoo (`ml_training/`) - Architectural Manual

---

## 1. Room Scope & Purpose

`ml_training` houses the offline machine learning training harnesses, model zoo (M0-M4), error metric evaluations, and the automated Metamorphic Relations QA Gate (MR1-MR8).

### Locked Architectural Invariants
- **Chronological Data Partitioning (Constitution Principle V)**: Datasets MUST be split strictly chronologically into **70% Train / 15% Validation / 15% Test**. Random train/test splits or shuffling are strictly forbidden to eliminate lookahead bias and temporal leakage.
- **Empirical Calibration Factor (0.92)**: The 0.92 calibration factor is calculated exclusively on clean, clear-sky training days ($G_{\text{poa}} / G_{\text{clearsky}} > 0.95$ under high noon conditions). It must NEVER be fitted on validation or test partitions.
- **Clear-Sky Ratio Modeling**: Rather than predicting raw power directly, advanced models (M3/M4) predict the bounded clear-sky ratio:
  $$r = \text{clip}\left(\frac{P_{\text{actual}}}{P_{\text{clear\_sky}}}, 0.0, 1.1\right)$$
  At inference time, predicted power is reconstructed as $\hat{P} = \hat{r} \times P_{\text{clear\_sky}}$.
- **Monotone Constraints & Sample Weighting**:
  - `monotone_constraints`: `+1` for POA irradiance, `-1` for cloud cover, `-1` for ambient/cell temperature (satisfies MR1, MR2, MR3).
  - `sample_weight = clear_sky_kw`: Downweights low-light twilight samples and zeroes night samples during loss minimization.
- **Strict Ban on Python `pickle`**: Serializing model weights as `.pkl` or `.joblib` is strictly forbidden due to security vulnerabilities and lack of long-term portability. Models MUST be saved as:
  - `model.json`: Native JSON representation of model weights and tree splits.
  - `metadata.json`: Feature list, hyperparameter dictionary, training git commit hash, and validation metrics.
- **Metamorphic QA Promotion Gate**: No model artifact may be promoted to `models/ACTIVE/` without achieving $\ge 95\%$ pass rate across the 8 Metamorphic Relations (MR1-MR8).

---

## 2. Model Zoo Progression

| Model | Architecture | Description | Target |
| :--- | :--- | :--- | :--- |
| **M0** | 24h Persistence Baseline | Replays previous day's power adjusted for clear-sky ratio | Raw Power ($kW$) |
| **M1** | Regularized Linear Ridge | Baseline linear model with L2 regularization | Raw Power ($kW$) |
| **M2** | Standard LightGBM / XGBoost | Gradient boosted regression trees on raw features | Raw Power ($kW$) |
| **M3** | Clear-Sky Ratio LightGBM | Residual ratio model with thermal derating | Ratio $r \in [0.0, 1.1]$ |
| **M4** | Constrained Ratio XGBoost | Physics-guided XGBoost with monotone constraints & sample weights | Ratio $r \in [0.0, 1.1]$ |

---

## 3. Module Roster & Current Implementation Status

### `data_loader.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`load_training_dataset(processed_dir) -> Tuple[train_df, val_df, test_df]`**:
  - Loads processed hourly datasets from `data/processed/`.
  - Filters out records with quality flags `fault_suspect` and `missing`.
  - Splits chronologically at 70% and 85% timestamps.

### `train.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`train_xgboost_ratio_model(train_df, hyperparameters)`**:
  - Fits XGBoost regressor predicting target $r$.
  - Enforces `monotone_constraints` and passes `sample_weight = train_df['clear_sky_kw']`.

### `evaluate.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`evaluate_model_metrics(model, test_df) -> Dict[str, float]`**: Computes daytime RMSE, MAE, and NMAE (normalized by 5.0 kW inverter capacity).
- **`run_metamorphic_gate(model, test_df) -> Dict[str, bool]`**: Executes the MR1-MR8 metamorphic verification suite.

### `export.py` (Current Status: SKELETON CONTRACT - Sprint 2)
- **`export_model_artifact(model, metadata, output_dir)`**: Exports portable `model.json` and `metadata.json` to `models/ACTIVE/`.
