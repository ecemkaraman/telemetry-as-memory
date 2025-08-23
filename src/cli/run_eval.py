import argparse
import yaml
import random
import numpy as np
import pandas as pd

from tam.telemetry import stream
from tam.features import featurize
from tam.trust import score as trust_score
from tam.online import ClosedLoop
from tam.baseline import StaticBaseline
from tam.policy import decide_action
from tam.metrics import rolling_acc, adaptation_latency, fp_rate
from tam.io import write_rows, write_json


def weak_label(e):
    # Same as original: drift raises err_rate; "ERROR" logs label positive.
    return int(e["err_rate"] > 0.08 or "ERROR" in e["log"])


def run_once(cfg: dict, mode: str, seed: int):
    # --- Deterministic randomness (critical for reproducible figures) ---
    rng = np.random.default_rng(seed)
    random.seed(seed)

    # Back‑compat config (old names still work)
    T = cfg.get("ticks", cfg.get("T", 1000))
    drift_t = cfg.get("drift_tick", cfg.get("drift_t", 300))

    # Optional new blocks (default → disabled to preserve drift-only behavior)
    tel_cfg = cfg.get("telemetry", {})
    poison_cfg = cfg.get("poison", {})
    novel_cfg = cfg.get("novel", {})

    eff_drift_t = tel_cfg.get("drift_t", drift_t)

    poison_rate = poison_cfg.get("rate", 0.0)
    poison_label = poison_cfg.get("label", "ERROR forged")
    poison_source = poison_cfg.get("source", "untrusted")

    novel_t = novel_cfg.get("t", None)
    novel_token = novel_cfg.get("token", "ERROR disk full")

    # Model selection (unchanged)
    if mode == "closed":
        model = ClosedLoop(use_trust=True)
    else:
        model = StaticBaseline(retrain_every=cfg.get("retrain_every", 300))

    rows = []
    for t in range(T):
        # Pass rng so telemetry noise is reproducible
        e = stream(
            t,
            drift_t=eff_drift_t,
            rng=rng,
            poison_rate=poison_rate,
            poison_label=poison_label,
            poison_source=poison_source,
            novel_t=novel_t,
            novel_token=novel_token,
        )

        x = featurize(e)
        y = weak_label(e)
        tr = trust_score(e)

        if mode == "closed":
            feats = {**x, "err_rate": e["err_rate"]}
            p = model.predict_proba(feats)
            action = decide_action(p, tr)
            model.learn(feats, y, trust=tr)
            drift_flag = model.update_drift(e["err_rate"])
        else:
            p = model.step(x, y)
            action, drift_flag = "no_op", False

        rows.append(
            {
                "t": t,
                "cpu": e["cpu"],
                "err": e["err_rate"],
                "log": e["log"],
                "source": e.get("source", "trusted"),
                "y": y,
                "p": float(p),
                "trust": float(tr),
                "action": action,
                "drift": int(drift_flag),
            }
        )

    # Per-run summary (lock metric semantics)
    df = pd.DataFrame(rows)
    yhat, acc = rolling_acc(df, window=50)  # fixed window = 50
    df["yhat"], df["acc"] = yhat, acc
    summary = {
        "adapt_latency": adaptation_latency(
            df,
            eff_drift_t,
            acc_threshold=0.95,
            min_persist=20,
        ),
        "fp_rate": fp_rate(df),
    }
    return rows, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--mode", choices=["closed", "baseline"], required=True)
    ap.add_argument("--out-prefix", required=False)  # kept for back-compat
    args = ap.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    # Fail fast if YAML wasn't parsed
    if cfg is None:
        raise ValueError(f"Config file {args.config} could not be parsed as YAML.")

    seeds = cfg.get("seeds", [1])
    out_dir = cfg.get("out_dir", "results")

    all_summ = []
    for s in seeds:
        rows, summ = run_once(cfg, args.mode, s)
        # File layout stays the same as your original
        write_rows(f"{out_dir}/csv/{args.mode}_seed{s}.csv", rows)
        write_json(f"{out_dir}/metrics/{args.mode}_seed{s}.json", summ)
        all_summ.append({"seed": s, **summ})

    # Aggregate
    df = pd.DataFrame(all_summ)
    agg = {
        "adapt_latency_mean": float(df["adapt_latency"].mean()),
        "fp_rate_mean": float(df["fp_rate"].mean()),
        "n_runs": int(len(df)),
    }
    write_json(f"{out_dir}/metrics/{args.mode}_aggregate.json", agg)


if __name__ == "__main__":
    main()
