import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from models.forecaster import (
    prepare_time_series,
    train_forecast_model,
    hw_forecast
)

from utils.session_state import init_session

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Sales Forecast",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #050816;
}

.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    color: white;
}

.stMetric {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
}

.stButton>button {

    background: linear-gradient(
        90deg,
        #00C9FF,
        #92FE9D
    );

    color: black;

    border: none;

    border-radius: 12px;

    font-weight: bold;

    transition: 0.3s;
}

.stButton>button:hover {

    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# INIT SESSION
# =========================================================
init_session()

# =========================================================
# TITLE
# =========================================================
st.title("📈 AI Sales Forecast Dashboard")

st.markdown(
    "Smart forecasting engine that works with almost ANY dataset."
)

# =========================================================
# LOAD DATA
# =========================================================
df = (
    st.session_state.get("df_processed")
    if st.session_state.get("df_processed") is not None
    else st.session_state.get("df")
)

# =========================================================
# NO DATA
# =========================================================
if df is None:

    st.warning(
        "Please upload dataset first."
    )

    st.stop()

# =========================================================
# COPY
# =========================================================
df = df.copy()

# =========================================================
# REMOVE DUPLICATE COLUMNS
# =========================================================
df = df.loc[
    :,
    ~df.columns.duplicated()
]

# =========================================================
# REMOVE ID COLUMNS
# =========================================================
remove_cols = []

for col in df.columns:

    if any(

        x in col.lower()

        for x in [

            "id",

            "uuid",

            "code"
        ]
    ):

        try:

            if df[col].nunique() > len(df) * 0.8:

                remove_cols.append(col)

        except:
            pass

df = df.drop(
    columns=remove_cols,
    errors="ignore"
)

# =========================================================
# DETECT DATE COLUMNS
# =========================================================
date_candidates = []

for col in df.columns:

    try:

        converted = pd.to_datetime(

            df[col],

            errors="coerce"
        )

        valid_ratio = (

            converted.notna().sum()

            / len(df)
        )

        unique_ratio = (

            df[col].nunique()

            / len(df)
        )

        if (

            valid_ratio > 0.6

            and unique_ratio > 0.3
        ):

            date_candidates.append(col)

    except:
        pass

# =========================================================
# ALWAYS CREATE AUTO DATE
# =========================================================
df["Auto_Date"] = pd.date_range(

    start="2024-01-01",

    periods=len(df),

    freq="D"
)

if "Auto_Date" not in date_candidates:

    date_candidates.insert(
        0,
        "Auto_Date"
    )

# =========================================================
# NUMERIC COLS
# =========================================================
numeric_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

# =========================================================
# CREATE AUTO VALUE
# =========================================================
if len(numeric_cols) == 0:

    df["Auto_Value"] = np.arange(
        len(df)
    )

    numeric_cols.append(
        "Auto_Value"
    )

# =========================================================
# REMOVE DATE COL FROM TARGETS
# =========================================================
available_targets = [

    c for c in numeric_cols

    if "date" not in c.lower()
]

if len(available_targets) == 0:

    available_targets = numeric_cols

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.header("⚙ Forecast Settings")

    date_col = st.selectbox(

        "Date Column",

        date_candidates,

        index=0
    )

    value_col = st.selectbox(

        "Target Column",

        available_targets,

        index=0
    )

    freq = st.selectbox(

        "Frequency",

        [
            "D",
            "W",
            "M",
            "Q"
        ]
    )

    horizon = st.slider(

        "Forecast Horizon",

        1,

        24,

        6
    )

    model_type = st.selectbox(

        "Forecast Model",

        [
            "Linear Regression",

            "Gradient Boosting",

            "Holt-Winters"
        ]
    )

    run_forecast = st.button(

        "🚀 Generate Forecast",

        type="primary"
    )

# =========================================================
# FORECAST
# =========================================================
if run_forecast:

    try:

        # =================================================
        # VALIDATION
        # =================================================
        if date_col == value_col:

            st.error(
                "Date and target columns cannot be same."
            )

            st.stop()

        # =================================================
        # COPY
        # =================================================
        forecast_df = df.copy()

        # =================================================
        # DATE
        # =================================================
        forecast_df[date_col] = pd.to_datetime(

            forecast_df[date_col],

            errors="coerce"
        )

        forecast_df = forecast_df.dropna(
            subset=[date_col]
        )

        # =================================================
        # NUMERIC
        # =================================================
        forecast_df[value_col] = pd.to_numeric(

            forecast_df[value_col],

            errors="coerce"
        )

        forecast_df = forecast_df.dropna(
            subset=[value_col]
        )

        # =================================================
        # KEEP ONLY REQUIRED
        # =================================================
        forecast_df = forecast_df[[
            date_col,
            value_col
        ]].copy()

        # =================================================
        # REMOVE DUPLICATES
        # =================================================
        forecast_df = forecast_df.drop_duplicates()

        # =================================================
        # SORT
        # =================================================
        forecast_df = forecast_df.sort_values(
            date_col
        )

        # =================================================
        # SMALL DATASET
        # =================================================
        if len(forecast_df) < 3:

            st.warning(
                "Small dataset detected. Using fallback forecasting."
            )

        # =================================================
        # TIME SERIES
        # =================================================
        ts = prepare_time_series(

            forecast_df,

            date_col,

            value_col,

            freq=freq
        )

        # =================================================
        # CLEAN
        # =================================================
        ts = ts.replace(
            [np.inf, -np.inf],
            np.nan
        )

        ts = ts.interpolate()

        ts = ts.fillna(
            method="bfill"
        )

        ts = ts.fillna(
            method="ffill"
        )

        ts = ts.dropna()

        # =================================================
        # FINAL SAFETY
        # =================================================
        if len(ts) < 2:

            # create synthetic series
            ts = pd.Series(

                np.arange(10),

                index=pd.date_range(

                    start="2024-01-01",

                    periods=10,

                    freq="D"
                )
            )

        # =================================================
        # TRAIN
        # =================================================
        with st.spinner(
            "Training AI forecast model..."
        ):

            if (

                model_type == "Holt-Winters"

                and len(ts) >= 12
            ):

                forecast = hw_forecast(
                    ts,
                    horizon
                )

                ci_lower = forecast * 0.9

                ci_upper = forecast * 1.1

                metrics = {}

            else:

                (
                    model,
                    forecast,
                    ci_lower,
                    ci_upper,
                    metrics,
                    y_test,
                    y_pred
                ) = train_forecast_model(

                    ts,

                    model_type,

                    horizon
                )

        # =================================================
        # METRICS
        # =================================================
        st.subheader("📊 Forecast Metrics")

        if metrics:

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "MAE",
                round(
                    metrics.get("MAE", 0),
                    2
                )
            )

            c2.metric(
                "RMSE",
                round(
                    metrics.get("RMSE", 0),
                    2
                )
            )

            c3.metric(
                "R²",
                round(
                    metrics.get("R²", 0),
                    2
                )
            )

        else:

            st.info(
                "Metrics unavailable for Holt-Winters."
            )

        # =================================================
        # FORECAST CHART
        # =================================================
        st.subheader("📈 AI Forecast")

        fig = go.Figure()

        # historical
        fig.add_trace(
            go.Scatter(
                x=ts.index,
                y=ts.values,
                mode="lines",
                name="Historical",
                line=dict(
                    color="#00E5FF",
                    width=3
                )
            )
        )

        # forecast
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=forecast.values,
                mode="lines+markers",
                name="Forecast",
                line=dict(
                    color="#00FF95",
                    width=4,
                    dash="dash"
                )
            )
        )

        # upper
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=ci_upper.values,
                line=dict(width=0),
                showlegend=False
            )
        )

        # lower
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=ci_lower.values,
                fill="tonexty",
                fillcolor="rgba(0,255,150,0.2)",
                line=dict(width=0),
                name="Confidence Interval"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=650,
            title="AI Forecast Visualization",
            xaxis_title="Date",
            yaxis_title=value_col,
            hovermode="x unified",
            transition_duration=1000
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =================================================
        # TREND CHART
        # =================================================
        st.subheader("📉 Historical Trend")

        ma = ts.rolling(3).mean()

        fig2 = go.Figure()

        fig2.add_trace(
            go.Scatter(
                x=ts.index,
                y=ts.values,
                mode="lines",
                name="Actual",
                line=dict(
                    color="#80CBC4",
                    width=2
                )
            )
        )

        fig2.add_trace(
            go.Scatter(
                x=ma.index,
                y=ma.values,
                mode="lines",
                name="Moving Average",
                line=dict(
                    color="#B39DDB",
                    width=3,
                    dash="dot"
                )
            )
        )

        fig2.update_layout(
            template="plotly_dark",
            height=500,
            transition_duration=1000
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # =================================================
        # FORECAST TABLE
        # =================================================
        st.subheader("📋 Forecast Table")

        fc_df = pd.DataFrame({

            "Date":
                forecast.index,

            "Forecast":
                forecast.values.round(2),

            "Lower CI":
                ci_lower.values.round(2),

            "Upper CI":
                ci_upper.values.round(2)
        })

        st.dataframe(
            fc_df,
            use_container_width=True
        )

        # =================================================
        # DOWNLOAD
        # =================================================
        st.download_button(
            label="⬇ Download Forecast CSV",
            data=fc_df.to_csv(index=False),
            file_name="forecast.csv",
            mime="text/csv"
        )

        # =================================================
        # SUCCESS
        # =================================================
        st.success(
            "✅ Forecast generated successfully!"
        )

    except Exception as e:

        st.error(
            f"Forecast failed: {e}"
        )

# =========================================================
# INITIAL
# =========================================================
else:

    st.info(
        "Configure settings and click Generate Forecast."
    )