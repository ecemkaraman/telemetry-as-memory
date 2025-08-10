def preprocess(record):
    return {
        "cpu_norm": record["cpu"] / 100.0,
        "latency_norm": record["latency"] / 1000.0,
        "error_rate": record["errors"] / 10.0,
    }
