import re, mmh3


def metric_feats(e: dict):
    return {"cpu": float(e["cpu"]), "err_rate": float(e["err_rate"])}


def hash_log(text: str, D: int = 512):
    feats = {}
    for tok in re.findall(r"[a-z0-9_\.:-]+", text.lower()):
        k = f"h{mmh3.hash(tok, signed=False) % D}"
        feats[k] = feats.get(k, 0.0) + 1.0
    return feats


def featurize(e: dict):
    x = metric_feats(e)
    x.update(hash_log(e.get("log", "")))
    return x
