#!/usr/bin/env python3
import argparse
import os
import inspect
import yaml
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


# -----------------------------
# Config loading & validation
# -----------------------------
def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")
    text = open(path, "r", encoding="utf-8").read()
    if not text.strip():
        raise ValueError(f"Config is empty: {path}")

    # Support single- or multi-document YAML
    docs = list(yaml.safe_load_all(text))
    cfg = docs[0] if docs else None
    if cfg is None:
        raise ValueError(f"Config parsed to None: {path}")

    # Required top-level keys (with BC/aliases)
    # We'll compute effective values later, but validate presence of out_dir and retrain_every
    cfg.setdefault("out_dir", "results")
    cfg.setdefault("retrain_every", 300)

    # Defaults for backward compatibility
    cfg.setdefault("ticks", cfg.get("T", 1000))
    cfg.setdefault("drift_tick", cfg.get("drift_t", 300))
    cfg.setdefault("seeds", [1])

    # Optional nested blocks
    cfg.setdefault("telemetry", {})
    cfg.setdefault("poison", {})
    cfg.setdefault("novel", {})

    return cfg


# -----------------------------
# Labeling rule
# -----------------------------
def weak_label(e: dict) -> int:
    """Weak supervision: flags high error-rate or explicit ERROR tokens as positive.
    Naturally labels poisoned 'ERROR' logs as positive, which is fine for the poisoning scenario.
    """
    return int(e.get("err_rate", 0.0) > 0.08 or ("log" in e and "ERROR" in e["log"]))


# -----------------------------
# Stream call safety
# -----------------------------
def call_stream_safely(t: int, **kw):
    """Pass only kwargs that the current telemetry.stream actually accepts."""
    sig = inspect.signature(stream)
    allowed = {k: v for k, v in kw.items() if k in sig.parameters}
    return stream(t, **allowed)


# -----------------------------
# Single run
# -----------------------------
def run_once(cfg: dict, mode: str, seed: int):
    rng = np.random.default_rng(seed)

    # Effective knobs (BC with old fields)
    T = int(cfg.get("ticks", 1000))
    drift_t_top = int(cfg.get("drift_tick", 300))

    tel_cfg = cfg.get("telemetry", {})
    poison_cfg = cfg.get("poison", {})
    novel_cfg = cfg.get("novel", {})

    # Resolve telemetry/drift settings
    eff_drift_t = int(tel_cfg.get("drift_t", drift_t_top))

    # Poisoning settings (optional)
    poison_rate = float(poison_cfg.get("rate", 0.0))
    poison_label = poison_cfg.get("label", "ERROR forged")
    poison_source = poison_cfg.get("source", "untrusted")

    # Novel-incident settings (optional)
    novel_t = novel_cfg.get("t", None)
    if novel_t is not None:
        novel_t = int(novel_t)
    novel_token = novel_cfg.get("token", "ERROR disk full")

    # Choose model
    if mode == "closed":
        model = ClosedLoop(use_trust=True)
    else:
        model = StaticBaseline(retrain_every=int(cfg.get("retrain_every", 300)))

    rows = []
    for t in range(T):
        # Build kwargs but only pass what stream() supports
        e = call_stream_safely(
            t,
            drift_t=eff_drift_t,
            poison_rate=poison_rate,
            poison_label=poison_label,
            poison_source=poison_source,
            novel_t=novel_t,
            novel_token=novel_token,
            rng=rng,  # harmless if stream ignores it; useful if you add deterministic RNG
        )

        x = featurize(e)
        y = weak_label(e)
        tr = float(trust_score(e))

        if mode == "closed":
            feats = {**x, "err_rate": e.get("err_rate", 0.0)}
            p = float(model.predict_proba(feats))
            action = decide_action(p, tr)
            model.learn(feats, y, trust=tr)
            drift_flag = bool(model.update_drift(e.get("err_rate", 0.0)))
        else:
            # Baseline trains in batches; internal step returns probability for logging
            p = float(model.step(x, y))
            action, drift_flag = "no_op", False

        rows.append(
            {
                "t": t,
                "cpu": e.get("cpu", float("nan")),
                "err": e.get("err_rate", float("nan")),
                "log": e.get("log", ""),
                "source": e.get("source", "trusted"),
                "y": int(y),
                "p": p,
                "trust": tr,
                "action": action,
                "drift": int(drift_flag),
            }
        )

    # Per-run summary
    df = pd.DataFrame(rows)
    yhat, acc = rolling_acc(df)
    df["yhat"], df["acc"] = yhat, acc

    summary = {
        "adapt_latency": float(adaptation_latency(df, eff_drift_t)),
        "fp_rate": float(fp_rate(df)),
    }
    return rows, summary


# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser(description="Run TAM evaluation (closed vs baseline).")
    ap.add_argument("--config", required=True, help="Path to YAML config.")
    ap.add_argument(
        "--mode",
        choices=["closed", "baseline"],
        required=True,
        help="Which learner to run.",
    )
    ap.add_argument(
        "--out-prefix",
        required=True,
        help="Prefix for output file names (e.g., 'closed' or 'baseline').",
    )
    args = ap.parse_args()

    cfg = load_config(args.config)
    out_dir = cfg.get("out_dir", "results")
    os.makedirs(os.path.join(out_dir, "csv"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "metrics"), exist_ok=True)

    seeds = cfg.get("seeds", [1])
    all_summ = []

    for s in seeds:
        rows, summ = run_once(cfg, args.mode, int(s))
        csv_path = f"{out_dir}/csv/{args.out_prefix}_seed{s}.csv"
        met_path = f"{out_dir}/metrics/{args.out_prefix}_seed{s}.json"
        write_rows(csv_path, rows)
        write_json(met_path, summ)
        all_summ.append({"seed": int(s), **summ})

    # Aggregate summary
    df = pd.DataFrame(all_summ)
    agg = {
        "adapt_latency_mean": float(df["adapt_latency"].mean())
        if len(df)
        else float("nan"),
        "fp_rate_mean": float(df["fp_rate"].mean()) if len(df) else float("nan"),
        "n_runs": int(len(df)),
    }
    write_json(f"{out_dir}/metrics/{args.out_prefix}_aggregate.json", agg)

    print(f"[OK] Wrote {len(seeds)} runs to {out_dir}. Aggregate: {agg}")


if __name__ == "__main__":
    main()
