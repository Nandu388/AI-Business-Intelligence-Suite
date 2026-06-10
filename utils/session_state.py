import streamlit as st

def init_session():
    defaults = {
        "df": None,
        "df_processed": None,
        "target_col": None,
        "date_col": None,
        "churn_model": None,
        "churn_features": None,
        "forecast_model": None,
        "segments": None,
        "anomaly_flags": None,
        "model_metrics": {},
        "report_data": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val