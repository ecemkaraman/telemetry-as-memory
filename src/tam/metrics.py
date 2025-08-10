import numpy as np, pandas as pd


def rolling_acc(df: pd.DataFrame, w: int = 25):
    yhat = (df["p"] >= 0.5).astype(int)
    acc = (yhat == df["y"]).rolling(w, min_periods=1).mean()
    return yhat, acc


def adaptation_latency(df: pd.DataFrame, drift_t=300, k=50, alpha=0.9):
    pre = df[df["t"] < drift_t]["acc"].dropna()
    if pre.empty:
        return np.nan
    target = alpha * pre.mean()
    post = df[df["t"] >= drift_t].copy()
    post["acc_k"] = post["acc"].rolling(k, min_periods=1).mean()
    hit = post[post["acc_k"] >= target]
    return int(hit["t"].iloc[0] - drift_t) if not hit.empty else np.nan


def fp_rate(df: pd.DataFrame):
    yhat = (df["p"] >= 0.5).astype(int)
    return float(((yhat == 1) & (df["y"] == 0)).mean())
