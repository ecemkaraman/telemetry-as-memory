"""Compute Trust Score Based on Telemetry Data"""


def compute_trust(record):
    score = 1.0
    if record["cpu"] > 90 or record["errors"] > 10:
        score -= 0.5
    return max(score, 0.0)
