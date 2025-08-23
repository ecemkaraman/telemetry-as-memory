#!/usr/bin/env python3
# scripts/plot_results.py

import argparse
import os
import glob
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def ensure_dir(p: str) -> None:
    Path(p).mkdir(parents=True, exist_ok=True)


def load_concat(pattern: str) -> pd.DataFrame:
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No files matched pattern: {pattern}")
    frames = []
    for p in paths:
        df = pd.read_csv(p)
        # attach seed inferred from filename if possible
        seed = None
        try:
            # expects ..._seed<NUM>.csv
            base = os.path.basename(p)
            if "_seed" in base:
                seed_part = base.split("_seed", 1)[1]
                seed = int(seed_part.split(".", 1)[0])
        except Exception:
            seed = None
        if seed is not None and "seed" not in df.columns:
            df["seed"] = seed
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def derive_predictions_and_acc(
    df: pd.DataFrame, threshold: float, window: int
) -> pd.DataFrame:
    """Ensure df has yhat and acc. Compute from y and p if missing."""
    df = df.copy()
    if "yhat" not in df.columns:
        if not {"y", "p"}.issubset(df.columns):
            raise ValueError("CSV must contain either 'yhat' or both 'y' and 'p'.")
        df["yhat"] = (df["p"].astype(float) >= float(threshold)).astype(int)

    if "acc" not in df.columns:
        if "y" not in df.columns:
            raise ValueError("To compute rolling accuracy, need 'y' column.")
        corr = (df["y"].astype(int) == df["yhat"].astype(int)).astype(float)
        # rolling per-seed if seed exists, else global
        if "seed" in df.columns:
            df["acc"] = (
                corr.groupby(df["seed"])
                .rolling(window, min_periods=1)
                .mean()
                .reset_index(level=0, drop=True)
                .values
            )
        else:
            df["acc"] = corr.rolling(window, min_periods=1).mean().values
    return df


def plot_acc_timeline(
    base: pd.DataFrame, closed: pd.DataFrame, outpath: str, drift_tick: int | None
) -> None:
    plt.figure(figsize=(8, 4))

    # average across seeds for each tick (t)
    base_g = base.groupby("t", as_index=False)["acc"].mean()
    closed_g = closed.groupby("t", as_index=False)["acc"].mean()

    plt.plot(base_g["t"], base_g["acc"], label="Baseline", linewidth=2)
    plt.plot(closed_g["t"], closed_g["acc"], label="Closed loop", linewidth=2)

    if drift_tick is not None:
        plt.axvline(drift_tick, linestyle="--", linewidth=1)

    plt.xlabel("Tick")
    plt.ylabel("Rolling Accuracy")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def compute_fp_rate(df: pd.DataFrame) -> pd.DataFrame:
    """False positives defined as yhat==1 while y==0."""
    df = df.copy()
    if not {"y", "yhat"}.issubset(df.columns):
        raise ValueError("Need 'y' and 'yhat' to compute FP rate.")
    df["fp"] = ((df["yhat"].astype(int) == 1) & (df["y"].astype(int) == 0)).astype(int)

    if "seed" in df.columns:
        grp = df.groupby("seed")
        out = grp.apply(
            lambda g: pd.Series(
                {
                    "fp_rate": g["fp"].sum() / max(1, len(g)),
                }
            )
        ).reset_index()
    else:
        out = pd.DataFrame([{"seed": 0, "fp_rate": df["fp"].sum() / max(1, len(df))}])
    return out


def plot_fp_bars(base: pd.DataFrame, closed: pd.DataFrame, outpath: str) -> None:
    base_stats = compute_fp_rate(base)
    closed_stats = compute_fp_rate(closed)

    means = [base_stats["fp_rate"].mean(), closed_stats["fp_rate"].mean()]
    stds = [
        base_stats["fp_rate"].std(ddof=1) if len(base_stats) > 1 else 0.0,
        closed_stats["fp_rate"].std(ddof=1) if len(closed_stats) > 1 else 0.0,
    ]

    labels = ["Baseline", "Closed loop"]
    x = np.arange(len(labels))

    plt.figure(figsize=(5.5, 4))
    plt.bar(x, means, yerr=stds, capsize=5)
    plt.xticks(x, labels)
    plt.ylabel("False Positive Rate")
    plt.ylim(0, max(0.05, 1.1 * max(means + [0])))
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def detect_layout(results_root: str, scenario: str) -> tuple[str, str]:
    """Return (csv_dir, figs_dir). Prefer scenario-specific; fallback to flat."""
    csv_dir = os.path.join(results_root, scenario, "csv")
    figs_dir = os.path.join(results_root, scenario, "figs")
    if not os.path.isdir(csv_dir):
        # fallback to flat layout (older runs)
        csv_dir = os.path.join(results_root, "csv")
        figs_dir = os.path.join(results_root, "figs")
    ensure_dir(figs_dir)
    return csv_dir, figs_dir


def main():
    ap = argparse.ArgumentParser(description="Plot TAM evaluation results.")
    ap.add_argument(
        "--scenario",
        type=str,
        default="drift",
        help="Scenario name used under results/<scenario>/",
    )
    ap.add_argument(
        "--results-root", type=str, default="results", help="Root results directory."
    )
    ap.add_argument(
        "--drift-tick",
        type=int,
        default=None,
        help="Tick index at which drift occurs (draws a vertical line).",
    )
    ap.add_argument(
        "--roll-window",
        type=int,
        default=50,
        help="Rolling window (ticks) for accuracy.",
    )
    ap.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Decision threshold to convert p->yhat when needed.",
    )
    args = ap.parse_args()

    csv_dir, figs_dir = detect_layout(args.results_root, args.scenario)

    base_glob = os.path.join(csv_dir, "baseline_seed*.csv")
    closed_glob = os.path.join(csv_dir, "closed_seed*.csv")

    baseline_df = load_concat(base_glob)
    closed_df = load_concat(closed_glob)

    # Derive yhat/acc columns if missing
    baseline_df = derive_predictions_and_acc(
        baseline_df, args.threshold, args.roll_window
    )
    closed_df = derive_predictions_and_acc(closed_df, args.threshold, args.roll_window)

    # Plot accuracy timeline
    acc_path = os.path.join(figs_dir, "acc_timeline.png")
    plot_acc_timeline(
        baseline_df,
        closed_df,
        acc_path,
        args.drift_tck if hasattr(args, "drift_tck") else args.drift_tick,
    )

    # Plot FP rate comparison
    fp_path = os.path.join(figs_dir, "fp_rate.png")
    plot_fp_bars(baseline_df, closed_df, fp_path)

    print(f"[OK] Saved figures to:\n  {acc_path}\n  {fp_path}")


if __name__ == "__main__":
    main()
