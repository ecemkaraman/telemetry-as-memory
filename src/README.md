# Telemetry-as-Memory (TAM) – Code Overview

This folder contains the full implementation of the **Telemetry-as-Memory (TAM)** prototype, as described in the paper:

> **Telemetry-as-Memory (TAM): Using Observability Pipelines to Train Adaptive AI Systems**

The code maps the conceptual TAM pipeline (telemetry → trust → memory → adaptive learning → policy → metrics) into concrete Python modules.

---

## Core Modules

- `tam/telemetry.py` : Implements a synthetic Kubernetes-like telemetry generator with support for **concept drift**, **poisoned logs**, and **novel incident** injection.

- `tam/baseline.py`  
  Implements the **offline retraining baseline** (e.g., logistic regression retrained every _N_ ticks).

- `tam/online.py`  
  Implements the **closed-loop learner** with trust-weighted online updates and **drift detection** (e.g., ADWIN integration).

- `tam/trust.py`  
  Provides **trust scoring** functions based on source validity, schema compliance, and anomaly likelihood.

- `tam/policy.py`  
  Encodes threshold-based and bandit-style **decision policies** that map model predictions to automated actions.

- `tam/metrics.py`  
  Defines evaluation metrics: rolling accuracy, adaptation latency, false-positive rate, and recovery iterations.

---

## Experiment Utilities

- `cli/run_eval.py`  
  Experiment runner for all scenarios (**concept drift**, **poisoned logs**, **novel incident**). Orchestrates the full loop over ticks, wiring telemetry, trust, models, policy, and metrics.

- `../scripts/plot_results.py`  
  Post-processing utilities for aggregating results and generating evaluation figures (accuracy vs. time, FP vs. time, etc.).

---

## Execution Flow

The overall flow implemented in this folder is:

1. **Telemetry Generation:** Synthetic logs, metrics, and traces → `tam/telemetry.py`

2. **Preprocessing and Trust Scoring:** Schema enforcement, source validation, and anomaly weighting → `tam/trust.py` (+ helpers in `tam/telemetry.py`)

3. **Featurization and Memory:** Rule-based tokens, hashing vectorizers, optional embeddings and memory-like representations → `tam/features.py`, `tam/telemetry.py`

4. **Adaptive Learning:** Online / meta-learning models with drift detection and trust-weighted updates → `tam/online.py`, `tam/drift.py`

5. **Inference and Action:** Predictions mapped to orchestration / automation calls via policy rules → `tam/policy.py`

6. **Governance and Explainability:** Approval gates, audit logging, and explainability checks; metric collection for analysis → `tam/online.py`, `tam/metrics.py`

7. **Experiment Execution:** Scenarios run via the experiment runner; results stored as CSV and JSON → `cli/run_eval.py`

8. **Visualization:** Evaluation figures produced from the stored results → `../scripts/plot_results.py`

---

## Implementation Flow Diagram

![Code Flow](https://raw.githubusercontent.com/ecemkaraman/telemetry-as-memory/main/figures/code_flow.png)

> **Figure – Implementation Flow (Code-Level).**  
> Mapping of the conceptual pipeline to concrete modules in the TAM prototype.  
> **Blue** = online learner, **Gray** = offline baseline, **Green** = policy, **Purple** = metrics/IO, **Dashed** = optional or internal.  
> Entry points orchestrate experiments (`cli/run_eval.py`) and visualization (`scripts/plot_results.py`).

