import pandas as pd
import numpy as np

from sklearn.cluster import KMeans

from sklearn.preprocessing import (
    StandardScaler,
    LabelEncoder
)

from sklearn.decomposition import PCA

from sklearn.metrics import (
    silhouette_score
)

import warnings

warnings.filterwarnings("ignore")

# =========================================================
# CLEAN FEATURES
# =========================================================
def clean_segmentation_data(
    df,
    feature_cols
):

    data = df.copy()

    valid_cols = []

    encoders = {}

    # =====================================================
    # HANDLE COLUMNS
    # =====================================================
    for col in feature_cols:

        if col not in data.columns:
            continue

        try:

            # categorical
            if data[col].dtype == object:

                data[col] = (
                    data[col]
                    .astype(str)
                    .fillna("Missing")
                )

                le = LabelEncoder()

                data[col] = le.fit_transform(
                    data[col]
                )

                encoders[col] = le

            else:

                data[col] = pd.to_numeric(
                    data[col],
                    errors="coerce"
                )

                median_val = data[col].median()

                if pd.isna(median_val):
                    median_val = 0

                data[col] = data[col].fillna(
                    median_val
                )

            valid_cols.append(col)

        except:
            pass

    # =====================================================
    # NO VALID COLS
    # =====================================================
    if len(valid_cols) == 0:

        return pd.DataFrame(), []

    # =====================================================
    # REMOVE CONSTANT COLS
    # =====================================================
    nunique = data[
        valid_cols
    ].nunique()

    valid_cols = nunique[
        nunique > 1
    ].index.tolist()

    if len(valid_cols) == 0:

        return pd.DataFrame(), []

    return data, valid_cols


# =========================================================
# FIND OPTIMAL K
# =========================================================
def find_optimal_k(

    X_scaled,

    k_range=range(2, 9)
):

    inertias = []

    sil_scores = []

    valid_k = []

    # =====================================================
    # LOOP
    # =====================================================
    for k in k_range:

        # avoid invalid cluster counts
        if k >= len(X_scaled):
            continue

        try:

            km = KMeans(

                n_clusters=k,

                random_state=42,

                n_init=20
            )

            labels = km.fit_predict(
                X_scaled
            )

            inertia = km.inertia_

            # safe silhouette
            try:

                sil = silhouette_score(
                    X_scaled,
                    labels
                )

            except:

                sil = 0

            inertias.append(inertia)

            sil_scores.append(sil)

            valid_k.append(k)

        except:
            pass

    return (
        valid_k,
        inertias,
        sil_scores
    )


# =========================================================
# RUN SEGMENTATION
# =========================================================
def run_segmentation(

    df,

    feature_cols,

    n_clusters=4
):

    # =====================================================
    # CLEAN
    # =====================================================
    data, feature_cols = clean_segmentation_data(

        df,

        feature_cols
    )

    # =====================================================
    # EMPTY
    # =====================================================
    if len(feature_cols) == 0:

        raise ValueError(
            "No valid feature columns."
        )

    # =====================================================
    # FEATURES
    # =====================================================
    X = data[
        feature_cols
    ].copy()

    # =====================================================
    # SMALL DATASET
    # =====================================================
    if len(X) < 3:

        raise ValueError(
            "Dataset too small for clustering."
        )

    # =====================================================
    # SAFE CLUSTERS
    # =====================================================
    n_clusters = min(

        n_clusters,

        max(2, len(X) // 2)
    )

    # =====================================================
    # SCALING
    # =====================================================
    try:

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(
            X
        )

    except:

        X_scaled = X.values

    # =====================================================
    # KMEANS
    # =====================================================
    km = KMeans(

        n_clusters=n_clusters,

        random_state=42,

        n_init=20
    )

    labels = km.fit_predict(
        X_scaled
    )

    # =====================================================
    # RESULT
    # =====================================================
    result = data.copy()

    result["Segment"] = labels

    # =====================================================
    # PCA
    # =====================================================
    try:

        n_components = min(
            2,
            X_scaled.shape[1]
        )

        pca = PCA(

            n_components=n_components,

            random_state=42
        )

        components = pca.fit_transform(
            X_scaled
        )

        result["PCA_1"] = (
            components[:, 0]
        )

        # if only one PCA dimension
        if n_components > 1:

            result["PCA_2"] = (
                components[:, 1]
            )

        else:

            result["PCA_2"] = 0

    except:

        result["PCA_1"] = np.arange(
            len(result)
        )

        result["PCA_2"] = 0

    # =====================================================
    # SILHOUETTE
    # =====================================================
    try:

        sil = silhouette_score(

            X_scaled,

            labels
        )

    except:

        sil = 0

    # =====================================================
    # SEGMENT SUMMARY
    # =====================================================
    try:

        segment_summary = (

            result.groupby("Segment")[

                feature_cols

            ]

            .mean()

            .round(2)
        )

    except:

        segment_summary = pd.DataFrame()

    # =====================================================
    # DISTANCE TO CENTER
    # =====================================================
    try:

        distances = km.transform(
            X_scaled
        )

        result["Distance_To_Center"] = (

            distances.min(axis=1)
        )

    except:
        pass

    # =====================================================
    # RETURN
    # =====================================================
    return (

        result,

        segment_summary,

        sil,

        km
    )