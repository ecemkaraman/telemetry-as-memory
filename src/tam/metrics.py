import numpy as np
import pandas as pd


def rolling_acc(df: pd.DataFrame, window: int = 50):
    """
    Rolling accuracy over a fixed window (locked for reproducibility).
    Expects columns: y (int), p (float in [0,1]).
    """
    y = df["y"].astype(int).to_numpy()
    yhat = (df["p"].to_numpy() >= 0.5).astype(int)
    acc = (
        pd.Series((yhat == y).astype(float))
        .rolling(window=window, min_periods=1)
        .mean()
        .to_numpy()
    )
    return yhat, acc


def adaptation_latency(
    df: pd.DataFrame,
    drift_t: int,
    acc_threshold: float = 0.95,
    min_persist: int = 20,
) -> float:
    """
    Latency from drift onset to first time rolling accuracy >= acc_threshold
    and stays there for at least `min_persist` steps.
    Returns ticks; if never satisfies, returns len(df) - drift_t.
    """
    acc = df["acc"].to_numpy()
    t = df["t"].to_numpy()
    # find index where t >= drift_t
    start_idx = np.searchsorted(t, drift_t, side="left")
    if start_idx >= len(acc):
        return float(len(df) - drift_t)
    for i in range(start_idx, len(acc)):
        if acc[i] >= acc_threshold:
            end = min(i + min_persist, len(acc))
            if np.all(acc[i:end] >= acc_threshold):
                return float(t[i] - drift_t)
    return float(t[-1] - drift_t)


def fp_rate(df: pd.DataFrame) -> float:
    """
    False positive rate using y (ground truth) vs yhat (thresholded p).
    """
    if "yhat" not in df.columns:
        yhat = (df["p"].to_numpy() >= 0.5).astype(int)
    else:
        yhat = df["yhat"].to_numpy().astype(int)
    y = df["y"].to_numpy().astype(int)
    negatives = y == 0
    if negatives.sum() == 0:
        return 0.0
    return float(((yhat == 1) & negatives).sum() / negatives.sum())
