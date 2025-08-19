# `src/tam/` – Core Modules

This folder contains the building blocks of the **Telemetry-as-Memory (TAM)** framework.

- **`baseline.py`** → Implements static offline learner retrained periodically (comparison baseline).
- **`features.py`** → Extracts features from logs/metrics, includes embedding & vectorization hooks.
- **`io.py`** → Handles input/output utilities (loading, saving, streaming traces).
- **`memory.py`** → Short-term sliding buffer + long-term vector memory for recall.
- **`metrics.py`** → Aggregates evaluation metrics (adaptation latency, FP/FN rates, drift recall).
- **`online.py`** → Trust-gated online learner with incremental updates + drift adaptation.
- **`policy.py`** → Defines threshold and bandit-style policies mapping predictions to actions.
- **`telemetry.py`** → Synthetic telemetry generator (CPU, error rates, logs, with injected drift).
- **`trust.py`** → Trust scoring logic to filter/block poisoned or unreliable telemetry.
- **`__init__.py`** → Makes `tam` a package for imports.
