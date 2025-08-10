import pandas as pd, matplotlib.pyplot as plt, glob, os, json

os.makedirs("results/figs", exist_ok=True)


def load_concat(pattern):
    frames = []
    for p in glob.glob(pattern):
        frames.append(pd.read_csv(p))
    return pd.concat(frames, ignore_index=True)


base = load_concat("results/csv/baseline_seed*.csv")
closed = load_concat("results/csv/closed_seed*.csv")

# Rolling accuracy over time
for df in (base, closed):
    df["yhat"] = (df["p"] >= 0.5).astype(int)
    df["acc"] = (df["yhat"] == df["y"]).rolling(25, min_periods=1).mean()

plt.figure()
plt.plot(base["t"], base["acc"], label="Baseline")
plt.plot(closed["t"], closed["acc"], label="Closed loop")
plt.axvline(300, linestyle="--", linewidth=1)
plt.xlabel("Ticks")
plt.ylabel("Rolling accuracy")
plt.legend()
plt.tight_layout()
plt.savefig("results/figs/acc_timeline.png", dpi=300)


# FP rate bars (aggregate JSON if present)
def agg_metric(name):
    p = f"results/metrics/{name}_aggregate.json"
    return json.load(open(p))["fp_rate_mean"] if os.path.exists(p) else None


bars = {"Baseline": agg_metric("baseline"), "Closed loop": agg_metric("closed")}
labels, vals = zip(*[(k, v if v is not None else 0.0) for k, v in bars.items()])

plt.figure()
plt.bar(labels, vals)
plt.ylabel("False positive rate (mean)")
plt.tight_layout()
plt.savefig("results/figs/fp_rate.png", dpi=300)
