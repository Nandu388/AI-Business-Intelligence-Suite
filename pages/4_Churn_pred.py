import streamlit as st
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px

from utils.session_state import init_session

from models.churn_model import (
    train_churn_model,
    predict_single
)

from utils.visualizer import (
    feature_importance_bar,
    pie_chart,
    churn_gauge,
    style_fig
)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Customer Churn Prediction",
    layout="wide"
)

# =====================================================
# INIT SESSION
# =====================================================
init_session()

st.title("🔮 Customer Churn Prediction")

# =====================================================
# LOAD DATA
# =====================================================
df = (
    st.session_state.df_processed
    if st.session_state.get("df_processed") is not None
    else st.session_state.get("df")
)

# =====================================================
# CHECK DATA
# =====================================================
if df is None:

    st.warning(
        "Please upload and preprocess data first."
    )

    st.stop()

# =====================================================
# AUTO DETECT / CREATE TARGET COLUMN
# =====================================================
possible_targets = []

for col in df.columns:

    unique_vals = df[col].dropna().unique()

    # ---------------------------------------------
    # Binary numeric columns
    # ---------------------------------------------
    if set(unique_vals).issubset({0, 1}):

        possible_targets.append(col)

    # ---------------------------------------------
    # Binary categorical columns
    # ---------------------------------------------
    elif len(unique_vals) == 2:

        possible_targets.append(col)

# =====================================================
# AUTO CREATE TARGET COLUMN
# =====================================================
if len(possible_targets) == 0:

    numeric_cols_temp = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    # remove id columns
    numeric_cols_temp = [

        c for c in numeric_cols_temp

        if "id" not in c.lower()
    ]

    if len(numeric_cols_temp) > 0:

        auto_col = numeric_cols_temp[0]

        threshold = df[auto_col].median()

        df["Auto_Churn"] = np.where(

            df[auto_col] > threshold,

            1,

            0
        )

        possible_targets.append(
            "Auto_Churn"
        )

# =====================================================
# NUMERIC COLUMNS
# =====================================================
num_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:

    st.header("⚙️ Churn Settings")

    # ---------------------------------------------
    # TARGET COLUMN
    # ---------------------------------------------
    target_col = st.selectbox(
        "Churn Target Column",
        possible_targets,
        key="target_column"
    )

    # ---------------------------------------------
    # FEATURE COLUMNS
    # ---------------------------------------------
    feature_cols = [

        c for c in num_cols

        if c != target_col
    ]

    default_features = (
        feature_cols[:8]
        if len(feature_cols) >= 8
        else feature_cols
    )

    selected_features = st.multiselect(
        "Feature Columns",
        feature_cols,
        default=default_features,
        key="feature_columns"
    )

    # ---------------------------------------------
    # MODEL TYPE
    # ---------------------------------------------
    model_type = st.selectbox(
        "Model",
        [
            "Random Forest",
            "Gradient Boosting",
            "Logistic Regression"
        ],
        key="model_type"
    )

    # ---------------------------------------------
    # SMOTE
    # ---------------------------------------------
    use_smote = st.checkbox(
        "Balance classes with SMOTE",
        value=True,
        key="smote_checkbox"
    )

    # ---------------------------------------------
    # TRAIN BUTTON
    # ---------------------------------------------
    train_btn = st.button(
        "🚀 Train Churn Model",
        type="primary"
    )

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3 = st.tabs([

    "📊 Model Performance",

    "📋 Churn Predictions",

    "🎯 Predict Single Customer"
])

# =====================================================
# TAB 1 — MODEL TRAINING
# =====================================================
with tab1:

    if train_btn:

        if len(selected_features) == 0:

            st.warning(
                "Please select feature columns."
            )

        else:

            with st.spinner(
                "Training churn model..."
            ):

                try:

                    (
                        model,
                        scaler,
                        metrics,
                        fpr,
                        tpr,
                        prec,
                        rec,
                        importances

                    ) = train_churn_model(

                        df,

                        target_col,

                        selected_features,

                        model_type,

                        use_smote
                    )

                    # =================================
                    # SAVE MODEL
                    # =================================
                    st.session_state.churn_model = model

                    st.session_state[
                        "churn_scaler"
                    ] = scaler

                    st.session_state[
                        "churn_features"
                    ] = selected_features

                    # =================================
                    # METRICS
                    # =================================
                    st.subheader(
                        "📈 Model Metrics"
                    )

                    c1, c2 = st.columns(2)

                    c1.metric(
                        "AUC-ROC",
                        round(
                            metrics["AUC-ROC"],
                            3
                        )
                    )

                    c2.metric(
                        "Accuracy",
                        f"{metrics['Accuracy']*100:.1f}%"
                    )

                    # =================================
                    # CLASSIFICATION REPORT
                    # =================================
                    st.subheader(
                        "📋 Classification Report"
                    )

                    report_df = pd.DataFrame(
                        metrics["Report"]
                    ).T.round(3)

                    st.dataframe(
                        report_df,
                        use_container_width=True
                    )

                    # =================================
                    # ROC CURVE
                    # =================================
                    c1, c2 = st.columns(2)

                    with c1:

                        roc_fig = go.Figure()

                        roc_fig.add_trace(

                            go.Scatter(

                                x=fpr,

                                y=tpr,

                                fill="tozeroy",

                                line=dict(
                                    color="#B39DDB"
                                ),

                                name=f"AUC={metrics['AUC-ROC']}"
                            )
                        )

                        roc_fig.add_trace(

                            go.Scatter(

                                x=[0, 1],

                                y=[0, 1],

                                mode="lines",

                                line=dict(
                                    dash="dash"
                                ),

                                name="Random"
                            )
                        )

                        roc_fig.update_layout(
                            title="ROC Curve",
                            template="plotly_dark"
                        )

                        st.plotly_chart(
                            roc_fig,
                            use_container_width=True
                        )

                    # =================================
                    # CONFUSION MATRIX
                    # =================================
                    with c2:

                        cm = metrics[
                            "Confusion Matrix"
                        ]

                        cm_fig = px.imshow(
                            cm,
                            text_auto=True,
                            title="Confusion Matrix"
                        )

                        cm_fig = style_fig(cm_fig)

                        st.plotly_chart(
                            cm_fig,
                            use_container_width=True
                        )

                    # =================================
                    # FEATURE IMPORTANCE
                    # =================================
                    if importances:

                        st.subheader(
                            "📊 Feature Importance"
                        )

                        st.plotly_chart(

                            feature_importance_bar(

                                list(importances.keys()),

                                list(importances.values())
                            ),

                            use_container_width=True
                        )

                    st.success(
                        "✅ Model trained successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"Training failed: {e}"
                    )

                    st.exception(e)

    else:

        st.info(
            "Configure settings and click "
            "'Train Churn Model'."
        )

# =====================================================
# TAB 2 — PREDICTIONS
# =====================================================
with tab2:

    if (
        st.session_state.get("churn_model")
        is not None
    ):

        try:

            model = st.session_state.churn_model

            scaler = st.session_state.get(
                "churn_scaler"
            )

            features = st.session_state.get(
                "churn_features"
            )

            # =========================================
            # PREPARE DATA
            # =========================================
            df_pred = df.copy()

            X = df_pred[
                features
            ].dropna()

            X_scaled = scaler.transform(X)

            probs = model.predict_proba(
                X_scaled
            )[:, 1]

            df_pred = df_pred.loc[
                X.index
            ].copy()

            # =========================================
            # ADD PREDICTIONS
            # =========================================
            df_pred[
                "Churn_Probability"
            ] = probs.round(4)

            df_pred[
                "Churn_Risk"
            ] = pd.cut(

                probs,

                bins=[0, 0.3, 0.7, 1],

                labels=[
                    "Low",
                    "Medium",
                    "High"
                ]
            )

            df_pred[
                "Prediction"
            ] = np.where(

                probs >= 0.5,

                "Will Churn",

                "Will Retain"
            )

            # =========================================
            # FILTERS
            # =========================================
            c1, c2 = st.columns(2)

            risk_filter = c1.multiselect(

                "Filter by Risk",

                ["Low", "Medium", "High"],

                default=[
                    "High",
                    "Medium"
                ],

                key="risk_filter"
            )

            pred_filter = c2.multiselect(

                "Filter by Prediction",

                [
                    "Will Churn",
                    "Will Retain"
                ],

                default=[
                    "Will Churn"
                ],

                key="prediction_filter"
            )

            # =========================================
            # FILTER DATA
            # =========================================
            df_show = df_pred[

                df_pred["Churn_Risk"].isin(
                    risk_filter
                )

                &

                df_pred["Prediction"].isin(
                    pred_filter
                )
            ]

            # =========================================
            # TABLE
            # =========================================
            st.subheader(
                "📋 Customer Predictions"
            )

            st.dataframe(

                df_show[
                    features
                    + [
                        "Churn_Probability",
                        "Churn_Risk",
                        "Prediction"
                    ]
                ],

                use_container_width=True
            )

            # =========================================
            # PIE CHARTS
            # =========================================
            c1, c2 = st.columns(2)

            with c1:

                vc = df_pred[
                    "Prediction"
                ].value_counts()

                st.plotly_chart(

                    pie_chart(
                        vc.index.tolist(),
                        vc.values.tolist(),
                        "Prediction Distribution"
                    ),

                    use_container_width=True
                )

            with c2:

                vc2 = df_pred[
                    "Churn_Risk"
                ].value_counts()

                st.plotly_chart(

                    pie_chart(
                        vc2.index.tolist(),
                        vc2.values.tolist(),
                        "Risk Distribution"
                    ),

                    use_container_width=True
                )

            # =========================================
            # HISTOGRAM
            # =========================================
            st.subheader(
                "📈 Churn Probability Distribution"
            )

            hist_fig = px.histogram(

                df_pred,

                x="Churn_Probability",

                nbins=40
            )

            hist_fig = style_fig(hist_fig)

            st.plotly_chart(
                hist_fig,
                use_container_width=True
            )

            # =========================================
            # DOWNLOAD
            # =========================================
            st.download_button(

                "⬇️ Download Predictions CSV",

                df_show.to_csv(index=False),

                "churn_predictions.csv",

                "text/csv"
            )

        except Exception as e:

            st.error(
                f"Prediction error: {e}"
            )

            st.exception(e)

    else:

        st.info(
            "Train the churn model first."
        )

# =====================================================
# TAB 3 — SINGLE CUSTOMER
# =====================================================
with tab3:

    if (
        st.session_state.get("churn_model")
        is not None
    ):

        features = st.session_state.get(
            "churn_features"
        )

        scaler = st.session_state.get(
            "churn_scaler"
        )

        st.subheader(
            "Enter Customer Values"
        )

        input_dict = {}

        cols = st.columns(3)

        for i, f in enumerate(features):

            min_v = float(df[f].min())

            max_v = float(df[f].max())

            mean_v = float(df[f].mean())

            input_dict[f] = cols[
                i % 3
            ].number_input(

                f,

                value=mean_v,

                min_value=min_v,

                max_value=max_v,

                key=f"input_{f}"
            )

        # =============================================
        # PREDICT BUTTON
        # =============================================
        if st.button(
            "🔮 Predict Customer",
            type="primary"
        ):

            prob, label = predict_single(

                st.session_state.churn_model,

                scaler,

                features,

                input_dict
            )

            c1, c2 = st.columns(2)

            with c1:

                st.plotly_chart(

                    churn_gauge(prob),

                    use_container_width=True
                )

            with c2:

                st.subheader(label)

                st.metric(
                    "Churn Probability",
                    f"{prob*100:.1f}%"
                )

                risk = (
                    "High"
                    if prob > 0.7
                    else "Medium"
                    if prob > 0.3
                    else "Low"
                )

                st.metric(
                    "Risk Level",
                    risk
                )

    else:

        st.info(
            "Train the churn model first."
        )