# Telemetry-as-Memory (TAM)

Modern observability pipelines collect logs, metrics, and traces at scale, but they remain largely **passive**: they monitor and alert, yet fail to adapt or learn in real time. ML in operations is often retrained offline, making it too slow to react to sudden changes and vulnerable to poisoned or noisy telemetry.

**Telemetry-as-Memory (TAM)** explores a different approach: treating observability data streams as live **adaptive memory** that continuously informs learning and action. The system is designed as a **closed loop**, where telemetry updates models online, trust scores filter unreliable inputs, and explainability gates ensure safe updates.

The goal is to lay the groundwork for **autonomous, secure, and explainable AIOps pipelines**—pipelines that adapt faster than static models, resist poisoning, and leverage past incidents to guide future decisions.

> **Note:** This repository presents the implementation highlights. The full research paper is currently in the pre-publication stage and will be submitted to **arXiv (August 2025)**.
> 

---

## Key Contributions

- **Telemetry as Adaptive Memory** → Logs + metrics + traces = live AI memory (continuous training input).
- **Trust-Gated Closed Loop** → Real-time updates weighted by trust scores to block poisoned telemetry.
- **Online Meta-Learning** → Rapid drift adaptation without requiring full retraining.
- **Explainability Gate** → Model updates are committed only when explainability (XAI) checks are reliable.
- **Observability + LLM + RL** → Hybrid agent design enabling autonomous and safeguarded remediation.

## Core Components

**1. Ingestion Layer**

- Collect logs, metrics, and traces via OpenTelemetry / cloud-native agents.
- Transported through Kafka/Event Hub/Kinesis to decouple producers & consumers.

**2. Preprocessing & Trust Scoring**

- Drop noise, mask PII, enforce schema.
- Assign **trust scores** (auth + schema + anomaly likelihood) to block poisoned data.

**3. Featurization & Memory Encoding**

- Metrics → raw, deltas, rolling aggregates.
- Logs → token flags, hashing vectorizer; optional embeddings (SentenceTransformers + FAISS/Pinecone).
- Memory = **short-term buffer** + **long-term vector DB** for semantic recall.

**4. Adaptive Learning Layer**

- Online learners (River logistic regression, Hoeffding trees).
- Drift detection (ADWIN, DDM) triggers fast updates.
- Trust-weighted updates; meta-learning adapts features/learning rate.

**5. Inference & Action Layer**

- Predict incident probability; policy maps to actions (restart, scale, block, no-op).
- Executes via Kubernetes/runbooks; logs all actions for traceability.

**6. Governance & Explainability**

- Approval gates for high-impact changes.
- SHAP/LIME explainability checks before committing updates.
- Full audit trail of telemetry, trust, predictions, and actions.

**7. Feedback Loop**

- Actions change system → generates new telemetry → feeds back into ingestion.
- Creates a **closed loop** for continuous learning + adaptation.

---

## System Flow

<img width="600" height="1200" alt="image" src="https://github.com/ecemkaraman/telemetry-as-memory/blob/main/figures/tam.png" />


---

## State and Prior Work

- **Prior work** has addressed fragments: few-shot anomaly adaptation, drift-triggered retraining, cost optimization, or self-healing policies.
- **Limitations:** none unify multi-channel telemetry (logs + metrics + traces) as adaptive memory, nor integrate security-first trust scoring with closed-loop online/meta-learning.
- **This work:** introduces a trust-gated, memory-augmented learning system that combines short-term adaptation with long-term semantic recall, enabling secure, explainable, closed-loop AIOps.

## Features

- **Synthetic Telemetry Generator** → Kubernetes-like stream of CPU, error rates, and logs with injected drift.
    
    [src/tam/telemetry.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/telemetry.py)
    
- **Baseline vs Closed-Loop Learners** → Compare static offline retraining with trust-gated online updates.
    
    [src/tam/baseline.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/baseline.py)
    
    [src/tam/online.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/online.py)
    
    Runner: [src/cli/run_eval.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/cli/run_eval.py)
    
- **Drift Detection** → ADWIN to trigger rapid adaptation under changing conditions.
    
    Detector: *planned* [src/tam/drift.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/drift.py) (in progress)
    
    Integrated into [src/tam/online.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/online.py)
    
- **Memory Integration** → Short-term sliding buffer + long-term semantic recall for logs.
    
    Short-term: [src/tam/memory.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/memory.py)
    
    Embeddings/vector DB hooks: [src/tam/features.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/features.py)
    
- **Security Gate** → Trust scores to block poisoned/unverified telemetry from influencing updates.
    
    [src/tam/trust.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/trust.py) (scoring logic)
    
    Applied in [src/tam/online.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/online.py)
    
- **Action Layer** → Threshold and bandit-style policies that map predictions to automated system actions.
    
    [src/tam/policy.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/tam/policy.py)
    
    Invoked via [src/cli/run_eval.py](https://github.com/ecemkaraman/telemetry-as-memory/blob/main/src/cli/run_eval.py)
