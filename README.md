# Telemetry-as-Memory (TAM)

> **Telemetry-as-Memory (TAM): Using Observability Pipelines to Train Adaptive AI Systems**

Observability pipelines such as OpenTelemetry and Prometheus collect logs, metrics, and traces at scale, but are largely **passive**: they power dashboards and alerts rather than training adaptive systems. Operational models are typically retrained offline on stale data, making them brittle to **drift** and vulnerable to **poisoned telemetry**.

**TAM** turns observability into an **adaptive memory substrate**. Telemetry is continuously ingested, assigned trust scores, encoded as features/memory, and fed to online/meta-learning models that drive secure, self-healing AIOps pipelines.

---

## 1. What This Repo Contains

This repository hosts the **TAM prototype**, including:

- **Full Research Paper** – [`main.pdf`](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/paper/main.pdf)
- **Core engine** – [`src/`](https://github.com/ecemkaraman/telemetry-as-memory/tree/main/src) (online learner, trust, policy, metrics).  See [`src/README.md`](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/README.md) for a code-level walkthrough.
- **Experiments & results** – evaluation scenarios, CSV/JSON outputs, and plots.  
  See [`results.md`](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/results/README.md) for detailed metrics and hypotheses.

---

## 2. Problem & Gap

Modern systems have three disconnected islands:
1. **Observability** – OpenTelemetry / Prometheus-style pipelines **collect and visualize** telemetry but stop short of learning.
2. **Online / Meta-learning** – Streaming and meta-learning methods enable rapid adaptation, but are rarely embedded in production telemetry.
3. **AIOps / Automation** – Prototypes automate response, but often lack **trust, explainability, and adversarial robustness**.

TAM bridges this gap by:
- Making **online learning** a first-class citizen of observability pipelines.
- Adding **trust-scored, security-gated updates** to defend against poisoned or low-quality telemetry.
- Providing hooks for **governance and explainability** on top of adaptive policies.

---

## 3. TAM Overview

TAM is a modular, closed-loop pipeline that converts raw observability streams into adaptive signals for **online learning** and **secure decision-making**.

### 3.1 Pipeline Layers

1. **Ingestion:**  Logs capture system events; metrics record CPU/error rates; traces encode request paths. Telemetry arrives via OpenTelemetry / cloud-native collectors.

2. **Preprocessing & Trust Scoring:**  
   - Deduplication, schema validation, PII masking.  
   - Each event receives a **trust score** based on source validity,schema compliance and anomaly likelihood.  
   - High-trust signals weigh strongly; low-trust signals are downweighted or dropped.

3. **Featurization & Memory**  
   - Rolling aggregates/deltas for metrics.  
   - Token flags, hashing vectorizers, or semantic embeddings for logs.  
   - Optional hierarchical memory combining short-term sliding windows and long-term vector stores (e.g., FAISS/Pinecone) for recall.

4. **Adaptive Learning**  
   - Streaming models (e.g., logistic regression / Hoeffding trees in River).  
   - Drift detectors (e.g., ADWIN) flag distribution shifts and trigger reweighting or resets.  
   - **Trust-weighted updates** limit the influence of poisoned inputs.

5. **Inference & Action**  
   - Combine current features + recalled incidents to predict outcomes and choose actions: restart service, scale deployment, block IP, create ticket, etc.  
   - High-impact actions pass through **gates** or human review.

6. **Governance & Explainability**  
   - Approval gates and audit trails.  
   - Hooks for SHAP/LIME-style interpretability.  
   - Rollback-friendly design: unsafe updates can be reverted while maintaining throughput.

Together, these layers transform observability from a passive diagnostic tool into an **adaptive memory substrate**, continuously closing the loop between observation, learning, and action.

<img width="600" height="1200" alt="image" src="https://github.com/ecemkaraman/telemetry-as-memory/blob/main/figures/tam.png" />

---

## 4. Threat Model 

We assume adversaries can inject or manipulate telemetry but **do not** have full system control.

### 4.1 Key Risks

- **Poisoning** – Fake logs/metrics corrupt model memory or bias updates.  
- **Drift Exploitation** – Gradual distribution shifts normalize malicious activity.  
- **Adversarial Inputs** – Crafted logs/traces mislead anomaly detectors.  
- **Feedback Abuse** – Induced failures cause harmful adaptive loops (“drift spirals”).  
- **Privilege Escalation** – Abusing automated actions (scaling, firewall rules) for leverage.

### 4.2 Mitigations

TAM’s design addresses these via:

- **Trust scoring** (source, schema, anomaly-likelihood).  
- **Drift detection** and adaptive reweighting / resets.  
- **Security gates** for high-impact actions.  
- **Audit trails** tying decisions back to telemetry and trust scores.

---

## 5. Experiments & Results (Summary)

The prototype evaluates TAM under three stressors:

1. **Concept Drift**  
   - Error dynamics change mid-run (step increase).  
   - TAM recovers within **~27 ticks vs ~300** for the offline baseline (~10× faster) with ~4% FP.

2. **Poisoned Logs**  
   - Adversarial `ERROR` logs injected from low-trust sources.  
   - Trust scoring keeps **false positives < ~5%**, preserving accuracy, while the offline baseline overreacts.

3. **Novel Incidents**  
   - Previously unseen `"disk full"` patterns.  
   - TAM adapts within **tens of ticks**, avoiding blind spots until the next offline retrain.

Details, tables, and reproduction commands are in `results.md`.
