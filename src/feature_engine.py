"""
Feature Engineering Module.

Provides temporal feature extraction, RFM customer segmentation,
association rule mining, and anomaly detection via Isolation Forest.
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Temporal Features
# ---------------------------------------------------------------------------


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract Year, Month, Day, DayOfWeek, and YearMonth from Order Date."""
    df = df.copy()
    dt = df["Order Date"]
    df["Year"] = dt.dt.year
    df["Month"] = dt.dt.month
    df["Day"] = dt.dt.day
    df["DayOfWeek"] = dt.dt.dayofweek  # 0=Monday
    df["YearMonth"] = dt.dt.to_period("M").astype(str)
    return df


# ---------------------------------------------------------------------------
# RFM Segmentation
# ---------------------------------------------------------------------------

_RFM_SEGMENT_MAP = {
    r"[4-5][4-5]": "Champions",
    r"[2-5][3-5]": "Loyal",
    r"[3-5][1-2]": "Potential Loyalist",
    r"[4-5][0-1]": "Recent Customers",
    r"[3-3][3-3]": "Need Attention",
    r"[2-3][1-2]": "About to Sleep",
    r"[0-2][2-5]": "At Risk",
    r"[0-1][4-5]": "Can't Lose Them",
    r"[1-2][1-2]": "Hibernating",
    r"[0-1][0-1]": "Lost",
}


def _rfm_segment(row: pd.Series) -> str:
    """Map a two-character RF score string to a named segment."""
    score = str(int(row["R_Score"])) + str(int(row["F_Score"]))
    for pattern, label in _RFM_SEGMENT_MAP.items():
        if pd.Series([score]).str.match(pattern).iloc[0]:
            return label
    return "Other"


def compute_rfm(df: pd.DataFrame, snapshot_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Compute Recency-Frequency-Monetary metrics per customer.

    Parameters
    ----------
    df : DataFrame with columns ``Customer ID``, ``Order ID``, ``Order Date``, ``Sales``.
    snapshot_date : Reference date for recency. Defaults to max(Order Date) + 1 day.

    Returns
    -------
    DataFrame indexed by Customer ID with R/F/M values, quintile scores, and segment label.
    """
    if snapshot_date is None:
        snapshot_date = df["Order Date"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("Customer ID")
        .agg(
            Recency=("Order Date", lambda x: (snapshot_date - x.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Sales", "sum"),
        )
        .reset_index()
    )

    # Quintile scoring (1 = worst, 5 = best)
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1], duplicates="drop").astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]
    rfm["Segment"] = rfm.apply(_rfm_segment, axis=1)
    return rfm


# ---------------------------------------------------------------------------
# Association Rule Mining
# ---------------------------------------------------------------------------


def compute_association_rules(
    df: pd.DataFrame,
    min_support: float = 0.01,
    min_confidence: float = 0.3,
) -> pd.DataFrame:
    """Derive association rules from co-purchased Sub-Categories.

    Uses the FP-Growth algorithm via ``mlxtend``.

    Returns
    -------
    DataFrame of rules sorted by lift descending.
    """
    from mlxtend.frequent_patterns import fpgrowth, association_rules

    # Build basket: rows = orders, columns = sub-categories, values = bool
    basket = (
        df.groupby(["Order ID", "Sub-Category"])["Quantity"]
        .sum()
        .unstack()
        .fillna(0)
        .map(lambda x: x > 0)
    )

    frequent = fpgrowth(basket, min_support=min_support, use_colnames=True)
    if frequent.empty:
        return pd.DataFrame(columns=["antecedents", "consequents", "support", "confidence", "lift"])

    rules = association_rules(frequent, metric="confidence", min_threshold=min_confidence)
    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)
    return rules


# ---------------------------------------------------------------------------
# Anomaly Detection (Isolation Forest)
# ---------------------------------------------------------------------------


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """Flag anomalous transactions using Isolation Forest.

    Features used: Sales, Profit, Quantity, Discount.
    Adds boolean column ``Is_Anomaly`` to a copy of *df*.
    """
    from sklearn.ensemble import IsolationForest

    df = df.copy()
    features = df[["Sales", "Profit", "Quantity", "Discount"]].values
    iso = IsolationForest(contamination=contamination, random_state=42, n_jobs=-1)
    predictions = iso.fit_predict(features)  # 1 = inlier, -1 = outlier
    df["Is_Anomaly"] = predictions == -1
    return df
