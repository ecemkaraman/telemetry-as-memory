import pandas as pd, matplotlib.pyplot as plt, glob, os, json, sys

os.makedirs("results/figs", exist_ok=True)


def load_concat(pattern):
    files = sorted(glob.glob(pattern))
    if not files:
        return None
    return pd.concat([pd.read_csv(p) for p in files], ignore_index=True)


base = load_concat("results/csv/baseline_seed*.csv")
closed = load_concat("results/csv/closed_seed*.csv")

if base is None and closed is None:
    sys.exit("No CSVs found in results/csv/. Run the eval scripts first.")

# Rolling accuracy over time (plot whatever we have)
plt.figure()
plotted = False
if base is not None:
    base["yhat"] = (base["p"] >= 0.5).astype(int)
    base["acc"] = (base["yhat"] == base["y"]).rolling(25, min_periods=1).mean()
    plt.plot(base["t"], base["acc"], label="Baseline")
    plotted = True
if closed is not None:
    closed["yhat"] = (closed["p"] >= 0.5).astype(int)
    closed["acc"] = (closed["yhat"] == closed["y"]).rolling(25, min_periods=1).mean()
    plt.plot(closed["t"], closed["acc"], label="Closed loop")
    plotted = True

if plotted:
    plt.axvline(300, linestyle="--", linewidth=1)
    plt.xlabel("Ticks")
    plt.ylabel("Rolling accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/figs/acc_timeline.png", dpi=300)

# FP rate bars (include only available modes)
bars = {}


def fp_rate(df):
    return float((((df["p"] >= 0.5).astype(int) == 1) & (df["y"] == 0)).mean())


if base is not None:
    bars["Baseline"] = fp_rate(base)
if closed is not None:
    bars["Closed loop"] = fp_rate(closed)

if bars:
    plt.figure()
    plt.bar(list(bars.keys()), list(bars.values()))
    plt.ylabel("False positive rate (mean)")
    plt.tight_layout()
    plt.savefig("results/figs/fp_rate.png", dpi=300)
else:
    print("No data available to plot FP rate.")

print("Done. Figures (if any) saved under results/figs/")
