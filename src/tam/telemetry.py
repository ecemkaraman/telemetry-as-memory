# src/tam/telemetry.py

import math
import random
from typing import Optional, Dict, Any


def stream(
    t: int,
    *,
    drift_t: int = 300,
    # --- Scenario 2: Poisoned Logs (optional) ---
    poison_rate: float = 0.0,
    poison_label: str = "ERROR forged",
    poison_source: str = "untrusted",
    # --- Scenario 3: Novel Incident (optional) ---
    novel_t: Optional[int] = None,
    novel_token: str = "ERROR disk full",
) -> Dict[str, Any]:
    """
    Generate a single telemetry event at tick t.

    Scenarios:
      1) Concept Drift:
         - err_rate mean jumps after `drift_t`.

      2) Poisoned Logs (optional):
         - With probability `poison_rate`, replace the log with `poison_label`
           and mark `source=poison_source`. Use trust scoring to block/weight.

      3) Novel Incident (optional):
         - After `novel_t`, override the log with `novel_token` to simulate a
           previously unseen pattern (e.g., "disk full").

    Precedence if multiple are configured:
      - Natural event (including drift) is generated first.
      - If a poison event is sampled, override log + mark untrusted source.
      - Else, if t >= novel_t, override log with the novel token.
    """

    # --- Base dynamics (original behavior) ---
    base_cpu = 40 + 15 * math.sin(t / 25)
    err_bump = 0.15 if t >= drift_t else 0.0

    # Error rate with small Gaussian noise; clamp at 0
    err = max(0.0, random.gauss(0.02 + err_bump, 0.01))

    # Map error rate to a coarse log level (original thresholds)
    if err < 0.05:
        log = "INFO ok"
    elif err < 0.12:
        log = "WARN retries"
    else:
        log = "ERROR timeout"

    source = "trusted"

    # --- Scenario 2: Poisoned Logs ---
    if poison_rate > 0.0 and random.random() < poison_rate:
        log = poison_label
        source = poison_source

    # --- Scenario 3: Novel Incident ---
    elif novel_t is not None and t >= novel_t:
        log = novel_token
        # source remains "trusted" for genuine novel incidents

    return {
        "tick": t,
        "cpu": base_cpu + random.uniform(-5, 5),
        "err_rate": err,
        "log": log,
        "source": source,
    }
