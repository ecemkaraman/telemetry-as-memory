import argparse, yaml, numpy as np, pandas as pd
from tam.telemetry import stream
from tam.features import featurize
from tam.trust import score as trust_score
from tam.online import ClosedLoop
from tam.baseline import StaticBaseline
from tam.policy import decide_action
from tam.metrics import rolling_acc, adaptation_latency, fp_rate
from tam.io import write_rows, write_json


def weak_label(e):
    return int(e["err_rate"] > 0.08 or "ERROR" in e["log"])


def run_once(cfg: dict, mode: str, seed: int):
    rng = np.random.default_rng(seed)
    T, drift_t = cfg["ticks"], cfg["drift_tick"]

    if mode == "closed":
        model = ClosedLoop(use_trust=True)
    else:
        model = StaticBaseline(retrain_every=cfg["retrain_every"])

    rows = []
    for t in range(T):
        e = stream(t, drift_t=drift_t)  # deterministic enough for demo
        x = featurize(e)
        y = weak_label(e)
        tr = trust_score(e)

        if mode == "closed":
            p = model.predict_proba({**x, "err_rate": e["err_rate"]})
            action = decide_action(p, tr)
            model.learn({**x, "err_rate": e["err_rate"]}, y, trust=tr)
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
                "y": y,
                "p": float(p),
                "trust": float(tr),
                "action": action,
                "drift": int(drift_flag),
            }
        )

    # per-run summary
    df = pd.DataFrame(rows)
    yhat, acc = rolling_acc(df)
    df["yhat"], df["acc"] = yhat, acc
    summary = {"adapt_latency": adaptation_latency(df, drift_t), "fp_rate": fp_rate(df)}
    return rows, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--mode", choices=["closed", "baseline"], required=True)
    ap.add_argument("--out-prefix", required=True)
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    seeds = cfg.get("seeds", [1])
    all_summ = []
    for s in seeds:
        rows, summ = run_once(cfg, args.mode, s)
        write_rows(f"{cfg['out_dir']}/csv/{args.mode}_seed{s}.csv", rows)
        write_json(f"{cfg['out_dir']}/metrics/{args.mode}_seed{s}.json", summ)
        all_summ.append({"seed": s, **summ})

    # aggregate summary
    df = pd.DataFrame(all_summ)
    agg = {
        "adapt_latency_mean": float(df["adapt_latency"].mean()),
        "fp_rate_mean": float(df["fp_rate"].mean()),
        "n_runs": int(len(df)),
    }
    write_json(f"{cfg['out_dir']}/metrics/{args.mode}_aggregate.json", agg)


if __name__ == "__main__":
    main()
