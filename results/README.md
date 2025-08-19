# Results & Findings

This MVP validates the **Telemetry-as-Memory (TAM)** framework using a synthetic Kubernetes-like telemetry stream with controlled drift, poisoning, and novel incident scenarios.

## Evaluation Setup

* **Telemetry Generator (`src/tam/telemetry.py`)**

  * CPU% → sinusoidal baseline + injected spikes
  * Error Rate → drift injected at tick \~300
  * Logs → INFO/WARN/ERROR strings aligned with error conditions

* **Learners**

  * **Baseline (`src/tam/baseline.py`)** → retrains offline every N ticks
  * **Closed-Loop (`src/tam/closed_loop.py`)** → online logistic regression (River) with **trust-weighted updates**

* **Drift Detector (`src/tam/drift.py`)** → ADWIN

* **Policies (`src/tam/policy.py`)** → threshold-based, later adaptive

## Scenarios

1. **Concept Drift** → error rate suddenly increases (simulated drift).
2. **Poisoned Logs** → fake `"ERROR"` strings from untrusted sources.
3. **Novel Incident** → new pattern (`"disk full"`) unseen in training.

## Results

### 1. Rolling Accuracy vs Ticks (`results/figs/acc_timeline.png`)

* **Blue (Baseline):**

  * High accuracy pre-drift.
  * Post-drift (t ≈ 300) → accuracy collapses to 0%.
  * Recovers only after retrain (t ≈ 600).

* **Orange (Closed-Loop):**

  * Slight jitter (continuous updates).
  * Post-drift → rapid recovery in \~25–30 ticks.
  * Stabilizes to high accuracy long before baseline retrains.
 https://github.com/ecemkaraman/telemetry-as-memory/blob/main/results/figs/acc_timeline.png?raw=true<img width="1920" height="1440" alt="image" src="https://github.com/user-attachments/assets/f0ada5d8-ec39-4ed3-8dfb-034e4c4b39ee" />


**Comparison:** Closed-loop recovers **10× faster** than baseline.

---

### 2. False Positive Rate (`results/figs/fp_rate.png`)

* **Baseline:** Zero FPs (because it “does nothing” during drift).
* **Closed-Loop:** Small FP rate (\~3–4%) due to real-time actioning.

**Trade-off:** Slight FP cost, but vastly better uptime.
https://github.com/ecemkaraman/telemetry-as-memory/blob/main/results/figs/fp_rate.png?raw=true<img width="1920" height="1440" alt="image" src="https://github.com/user-attachments/assets/d4bd6c41-47df-49c9-b7b5-79f338ee458a" />


---

## Aggregate Metrics (`results/metrics/*.json`)

Example (Closed-Loop):

```json
{
  "adapt_latency_mean": 27.6,
  "fp_rate_mean": 0.041,
  "n_runs": 5
}
```

* **adapt\_latency\_mean** → avg ticks to recover post-drift (\~27.6 ticks).
* **fp\_rate\_mean** → false positives ≈ 4.1%.
* **n\_runs** → aggregated across 5 seeds.

Baseline shows latency \~300 ticks → \~80% slower recovery.

---

## File Outputs

* **`results/csv/*`** → per-tick traces (ground truth `y`, prediction `p`, trust score, drift flags, action).
* **`results/metrics/*`** → aggregated JSONs for adaptation speed & FP rate.
* **`results/figs/*`** → publication-ready figures.

---

# Key Findings

1. **Adaptation Speed:**

   * Baseline: \~300 ticks latency.
   * Closed-Loop: \~27 ticks latency.

2. **False Positives:**

   * Baseline: 0% (inactive during drift).
   * Closed-Loop: \~3–4% (acceptable trade-off for faster response).

3. **Resilience to Drift:**

   * Closed-Loop continuously learns → no retrain downtime.
   * Trust scoring mitigates poisoning by ignoring low-confidence logs.



