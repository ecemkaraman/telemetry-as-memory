import math, random


def stream(t: int, drift_t: int = 300):
    base_cpu = 40 + 15 * math.sin(t / 25)
    err_bump = 0.15 if t >= drift_t else 0.0
    err = max(0.0, random.gauss(0.02 + err_bump, 0.01))
    log = (
        "INFO ok" if err < 0.05 else ("WARN retries" if err < 0.12 else "ERROR timeout")
    )
    return {
        "tick": t,
        "cpu": base_cpu + random.uniform(-5, 5),
        "err_rate": err,
        "log": log,
    }
