import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

from sklearn.cluster import KMeans
from sklearn.preprocessing import (
    StandardScaler,
    LabelEncoder
)

from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.ensemble import IsolationForest

from utils.session_state import init_session

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Customer Segmentation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

[data-testid="metric-container"] {
    background: #1E1E2F;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# INIT
# =====================================================
init_session()

st.title("👥 Customer Segmentation Dashboard")

# =====================================================
# LOAD DATA
# =====================================================
df = (
    st.session_state.df_processed
    if st.session_state.get("df_processed") is not None
    else st.session_state.get("df")
)

if df is None:

    st.warning("Upload dataset first.")

    st.stop()

# =====================================================
# REMOVE DUPLICATES
# =====================================================
df = df.loc[:, ~df.columns.duplicated()]

# =====================================================
# ENCODE OBJECTS
# =====================================================
for col in df.columns:

    try:

        if df[col].dtype == "object":

            le = LabelEncoder()

            df[col] = le.fit_transform(
                df[col].astype(str)
            )

    except:
        pass

# =====================================================
# NUMERIC COLUMNS
# =====================================================
num_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

num_cols = [

    c for c in num_cols

    if "id" not in c.lower()
]

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:

    st.header("⚙️ Settings")

    feature_cols = st.multiselect(

        "Features",

        num_cols,

        default=num_cols[:4]
    )

    n_clusters = st.slider(
        "Clusters",
        2,
        10,
        4
    )

    anomaly_rate = st.slider(
        "Anomaly %",
        0.01,
        0.20,
        0.05
    )

    run_btn = st.button(
        "🚀 Run Analysis",
        type="primary"
    )

# =====================================================
# RUN
# =====================================================
if run_btn:

    if len(feature_cols) < 2:

        st.warning(
            "Select at least 2 features."
        )

        st.stop()

    try:

        # =================================================
        # DATA
        # =================================================
        seg_df = df[feature_cols].dropna()

        scaler = StandardScaler()

        scaled = scaler.fit_transform(
            seg_df
        )

        # =================================================
        # KMEANS
        # =================================================
        kmeans = KMeans(

            n_clusters=n_clusters,

            random_state=42,

            n_init=10
        )

        clusters = kmeans.fit_predict(
            scaled
        )

        seg_df["Segment"] = clusters

        # =================================================
        # PCA
        # =================================================
        pca = PCA(n_components=2)

        pca_result = pca.fit_transform(
            scaled
        )

        seg_df["PCA1"] = pca_result[:, 0]
        seg_df["PCA2"] = pca_result[:, 1]

        # =================================================
        # SILHOUETTE
        # =================================================
        sil_score = silhouette_score(
            scaled,
            clusters
        )

        # =================================================
        # ANOMALY
        # =================================================
        iso = IsolationForest(

            contamination=anomaly_rate,

            random_state=42
        )

        anomaly_pred = iso.fit_predict(
            scaled
        )

        seg_df["Anomaly"] = np.where(
            anomaly_pred == -1,
            "Anomaly",
            "Normal"
        )

        # =================================================
        # KPI ROW
        # =================================================
        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Rows",
            len(seg_df)
        )

        c2.metric(
            "Clusters",
            n_clusters
        )

        c3.metric(
            "Silhouette",
            round(sil_score, 3)
        )

        c4.metric(
            "Anomalies",
            (seg_df["Anomaly"] == "Anomaly").sum()
        )

        # =================================================
        # CHART ROW 1
        # =================================================
        col1, col2 = st.columns(2)

        with col1:

            scatter_fig = px.scatter(

                seg_df,

                x="PCA1",

                y="PCA2",

                color=seg_df["Segment"].astype(str),

                title="Customer Segments",

                height=500
            )

            scatter_fig.update_layout(
                template="plotly_dark"
            )

            st.plotly_chart(
                scatter_fig,
                use_container_width=True
            )

        with col2:

            seg_counts = seg_df[
                "Segment"
            ].value_counts()

            pie_fig = px.pie(

                values=seg_counts.values,

                names=[
                    f"Segment {i}"
                    for i in seg_counts.index
                ],

                title="Segment Distribution",

                height=500
            )

            pie_fig.update_layout(
                template="plotly_dark"
            )

            st.plotly_chart(
                pie_fig,
                use_container_width=True
            )

        # =================================================
        # CHART ROW 2
        # =================================================
        col3, col4 = st.columns(2)

        with col3:

            x_col = feature_cols[0]
            y_col = feature_cols[1]

            anomaly_fig = px.scatter(

                seg_df,

                x=x_col,

                y=y_col,

                color="Anomaly",

                title="Anomaly Detection",

                height=500
            )

            anomaly_fig.update_layout(
                template="plotly_dark"
            )

            st.plotly_chart(
                anomaly_fig,
                use_container_width=True
            )

        with col4:

            profile_df = seg_df.groupby(
                "Segment"
            )[feature_cols].mean()

            heatmap_fig = px.imshow(

                profile_df,

                text_auto=True,

                aspect="auto",

                title="Segment Heatmap"
            )

            heatmap_fig.update_layout(
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(
                heatmap_fig,
                use_container_width=True
            )

        # =================================================
        # TABLES INSIDE EXPANDER
        # =================================================
        with st.expander(
            "📋 View Detailed Data"
        ):

            st.dataframe(
                seg_df.head(200),
                use_container_width=True,
                height=400
            )

        # =================================================
        # DOWNLOAD
        # =================================================
        st.download_button(

            "⬇️ Download Results",

            seg_df.to_csv(index=False),

            "segmentation_results.csv",

            "text/csv"
        )

        st.success(
            "✅ Analysis completed successfully!"
        )

    except:

        st.warning(
            """
            Segmentation could not be performed
            on this dataset.
            """
        )

else:

    st.info(
        "Select features and click Run Analysis."
    )