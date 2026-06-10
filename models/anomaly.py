import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

import warnings

warnings.filterwarnings("ignore")

# =========================================================
# DETECT ANOMALIES
# =========================================================
def detect_anomalies(
    df,
    feature_cols,
    contamination=0.05
):

    # =====================================================
    # EMPTY CHECK
    # =====================================================
    if df is None or len(df) == 0:

        return pd.DataFrame()

    # =====================================================
    # VALID COLUMNS
    # =====================================================
    valid_cols = []

    for col in feature_cols:

        if col in df.columns:

            try:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

                valid_cols.append(col)

            except:
                pass

    # =====================================================
    # NO VALID COLUMNS
    # =====================================================
    if len(valid_cols) == 0:

        result = df.copy()

        result["Anomaly"] = 0
        result["Anomaly_Score"] = 0

        return result

    # =====================================================
    # FEATURE DATA
    # =====================================================
    X = df[valid_cols].copy()

    # =====================================================
    # CLEAN
    # =====================================================
    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # =====================================================
    # FILL MISSING
    # =====================================================
    for col in X.columns:

        median_val = X[col].median()

        if pd.isna(median_val):

            median_val = 0

        X[col] = X[col].fillna(
            median_val
        )

    # =====================================================
    # VERY SMALL DATASET
    # =====================================================
    if len(X) < 5:

        result = df.copy()

        result["Anomaly"] = 0

        result["Anomaly_Score"] = 0

        return result

    # =====================================================
    # REMOVE CONSTANT COLUMNS
    # =====================================================
    nunique = X.nunique()

    keep_cols = nunique[
        nunique > 1
    ].index.tolist()

    if len(keep_cols) == 0:

        result = df.copy()

        result["Anomaly"] = 0

        result["Anomaly_Score"] = 0

        return result

    X = X[keep_cols]

    # =====================================================
    # SAFE CONTAMINATION
    # =====================================================
    contamination = min(
        max(contamination, 0.001),
        0.5
    )

    # =====================================================
    # SCALING
    # =====================================================
    try:

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(X)

    except:

        X_scaled = X.values

    # =====================================================
    # MODEL
    # =====================================================
    try:

        iso = IsolationForest(

            contamination=contamination,

            random_state=42,

            n_estimators=200,

            bootstrap=True
        )

        preds = iso.fit_predict(
            X_scaled
        )

        scores = iso.score_samples(
            X_scaled
        )

    except:

        preds = np.ones(len(X_scaled))

        scores = np.zeros(len(X_scaled))

    # =====================================================
    # RESULT
    # =====================================================
    result = df.loc[X.index].copy()

    result["Anomaly"] = (
        preds == -1
    ).astype(int)

    # higher score = more anomalous
    result["Anomaly_Score"] = (
        -scores
    )

    # =====================================================
    # NORMALIZE SCORE
    # =====================================================
    try:

        score_min = result[
            "Anomaly_Score"
        ].min()

        score_max = result[
            "Anomaly_Score"
        ].max()

        if score_max != score_min:

            result["Anomaly_Score"] = (

                (
                    result["Anomaly_Score"]
                    - score_min
                )

                /

                (
                    score_max
                    - score_min
                )
            )

    except:
        pass

    # =====================================================
    # SORT
    # =====================================================
    result = result.sort_values(

        "Anomaly_Score",

        ascending=False
    )

    return result