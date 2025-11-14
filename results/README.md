# Evaluation & Results

##  Goals and Hypotheses

- **H1 (Adaptation speed).** Closed-loop TAM recovers from concept drift within an order of magnitude fewer ticks than offline retraining.  
- **H2 (Safety under attack).** Trust scoring reduces the influence of poisoned telemetry, keeping false positives \< 5%.  
- **H3 (Novel incident handling).** Memory-augmented learning adapts to unseen patterns (e.g., `"disk full"`) without retraining.

---

## Experimental Setup

- **Environment**
  - **CPU%:** sinusoidal baseline with injected spikes.  
  - **Error rate:** step increase at *t* ≈ 300 to induce drift.  
  - **Logs:** `INFO` / `WARN` / `ERROR` aligned with error conditions.

- **Models**
  - **Baseline:** Offline logistic regression retrained every *N* ticks (common in AIOps).  
  - **Closed-loop TAM:** River-based online logistic regression with trust-weighted updates.

- **Detection**  
  - ADWIN for drift detection; trust scores to downweight unverified telemetry.

- **Policy**  
  - Static thresholds; adaptive bandit-style left for future work.

- **Reproducibility**  
  - Experiments deterministic (fixed seeds); variance across runs ≈ \< 5% latency, \< 2% FP.

---

## Scenarios

- **Scenario 1 (H1 – Concept Drift).**  
  Error rate increases at *t* ≈ 300, making the baseline decision boundary stale.

- **Scenario 2 (H2 – Poisoned Logs).**  
  Inject synthetic `ERROR` messages from untrusted sources to test trust scoring.

- **Scenario 3 (H3 – Novel Incident).**  
  Introduce unseen `"disk full"` logs to test retrieval-augmented adaptation.

---

## Metrics

- **Primary**
  - Adaptation latency (ticks to recover).  
  - False positive rate (spurious actions).

- **Secondary**
  - False negatives, drift detection recall, action ROI, recovery iterations.

- **Emphasis**  
  - Primary metrics prioritized in analysis; secondary metrics defined but not collected in this prototype.

---

## Results

For each scenario, we show: (i) accuracy recovery and (ii) FP trade-offs.  
All results are averaged over 5 seeds. Variance across runs was modest (\< 5% latency, \< 2% FP).

---

## Scenario 1: Concept Drift (H1)

<table>
  <tr>
    <td width="50%">
      <img src="drift/figs/acc_timeline.png" alt="Figure 1: H1 – Accuracy under drift" />
    </td>
    <td width="50%">
      <img src="drift/figs/fp_rate.png" alt="Figure 2: H1 – FP rate" />
    </td>
  </tr>
</table>

*Figure 1 – H1: Accuracy under drift.*  
Baseline collapses after *t* ≈ 300 and recovers only at retrain (*t* ≈ 600). Closed-loop adapts within ~27 ticks, validating H1.

*Figure 2 – H1: FP rate.*  
Baseline ≈ 0% (inactive). Closed-loop ≈ 4% FP, an acceptable safety–adaptivity trade-off.

**Summary**

- Baseline model becomes stale after the drift point and remains inaccurate until the scheduled offline retrain.  
- TAM detects the shift and re-adapts in ~27 ticks, roughly an order of magnitude faster.  
- Closed-loop behavior introduces a small FP cost (~4%) but avoids hundreds of ticks of degraded performance.

---

## Scenario 2: Poisoned Logs (H2)

<table>
  <tr>
    <td width="50%">
      <img src="poison/figs/acc_timeline.png" alt="Figure 3: H2 – Accuracy under poisoning" />
    </td>
    <td width="50%">
      <img src="poison/figs/fp_rate.png" alt="Figure 4: H2 – FP rate" />
    </td>
  </tr>
</table>

*Figure 3 – H2: Accuracy under poisoning.*  
Baseline fails on fake `ERROR`s, while closed-loop trust scoring downweights untrusted sources and preserves accuracy (supports H2).

*Figure 4 – H2: FP rate.*  
Baseline FP spikes under poisoning. Closed-loop keeps FP \< 5% via trust-scored filtering.

**Summary**

- Injected adversarial `ERROR` logs cause the baseline to overreact and degrade.  
- TAM’s trust scoring filters or downweights low-trust telemetry, maintaining accuracy.  
- FP rate remains below the 5% target despite sustained poisoning attempts.

---

## Scenario 3: Novel Incident (H3)

<table>
  <tr>
    <td width="50%">
      <img src="novel/figs/acc_timeline.png" alt="Figure 5: H3 – Accuracy for unseen disk full" />
    </td>
    <td width="50%">
      <img src="novel/figs/fp_rate.png" alt="Figure 5: H3 – FP rate" />
    </td>
  </tr>
</table>

*Figure 5 – H3: Accuracy for unseen “disk full”.*  
Baseline fails until retrain. Closed-loop adapts within tens of ticks via online updates, confirming H3.

*Figure 6 – H3: FP rate.*  
Closed-loop incurs moderate FP while adapting, but recovers within \< 40 ticks despite moderate FP. Baseline remains inert until retrain.

**Summary**

- Novel `"disk full"` patterns are invisible to the baseline until a new training cycle.  
- TAM incorporates the new pattern through online learning and adapts within tens of ticks.  
- There is a brief FP spike during adaptation, but it stabilizes quickly, giving faster response to new failure modes.

---

## Overall Summary of Findings

Across the three scenarios, TAM demonstrates:

- **Concept Drift:** Recovery within ~27 ticks vs. 300+ for baselines (~10× faster), with false positives bounded around ~4%.  
- **Poisoned Logs:** Trust scoring blocks adversarial `ERROR` injections, maintaining stable accuracy where baselines degrade.  
- **Novel Incidents:** Unseen `"disk full"` patterns are handled within tens of ticks, avoiding blind spots until offline retrain.

These experiments validate **secure, trust-weighted online learning** for AIOps. Remaining risks include poisoning and drift manipulation at scale, but trust scoring and drift detection mitigate much of this risk, while governance and explainability remain key future extensions.
