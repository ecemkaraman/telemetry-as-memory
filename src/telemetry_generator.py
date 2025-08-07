"""
Aim: Simulate synthetic telemetry data that resembles logs and metrics from a microservices environment w/ anomalies (e.g., CPU spikes, latency jitter, error bursts)
"""

import random
import pandas as pd
from datetime import datetime, timedelta


def generate_telemetry(num_points=1000, anomaly=False):
    data = []
    ts = datetime.now()

    for i in range(num_points):
        cpu = random.gauss(40, 5)
        latency = random.gauss(100, 10)
        errors = random.randint(0, 2)

        if anomaly and i > num_points // 2:
            cpu += 30  # simulate spike
            latency += 50
            errors += 5

        data.append(
            {
                "timestamp": ts.isoformat(),
                "cpu": cpu,
                "latency": latency,
                "errors": errors,
                "service": "api-gateway",
            }
        )
        ts += timedelta(seconds=1)

    return pd.DataFrame(data)


# Example Use
if __name__ == "__main__":
    df = generate_telemetry(num_points=100, anomaly=True)
    print(df.head())
