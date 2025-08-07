def inject_drift(record, drift_type="latency_spike"):
    if drift_type == "latency_spike":
        record["latency"] += 200
    return record
