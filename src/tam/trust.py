TOK = {"error": 0.8, "warn": 0.4, "timeout": 0.7, "retry": 0.3}


def score(e: dict) -> float:
    s = 1.0
    t = e.get("log", "").lower()
    for k, w in TOK.items():
        if k in t:
            s += 0.2 * w
    if not (0 <= e.get("err_rate", 0) < 1):
        s *= 0.5
    if not (0 <= e.get("cpu", 0) <= 100):
        s *= 0.7
    return max(0.1, min(s, 2.0))
