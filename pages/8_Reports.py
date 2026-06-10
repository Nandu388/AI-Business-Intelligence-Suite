import streamlit as st
import pandas as pd
import datetime

from utils.session_state import init_session
from utils.report_gen import (
    to_excel_bytes,
    to_pdf_bytes
)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide"
)

# =====================================================
# INIT SESSION
# =====================================================
init_session()

# =====================================================
# TITLE
# =====================================================
st.title("📄 Reports")

st.caption(
    "Generate professional reports from your AI BI analysis."
)

# =====================================================
# LOAD DATA
# =====================================================
df = (
    st.session_state.get("df_processed")
    if st.session_state.get("df_processed") is not None
    else st.session_state.get("df")
)

report_data = st.session_state.get(
    "report_data",
    {}
)

# =====================================================
# CHECK DATA
# =====================================================
if df is None:

    st.warning(
        "Please upload data first."
    )

    st.stop()

# =====================================================
# REPORT SECTIONS
# =====================================================
sections = []

# =====================================================
# SECTION 1 — DATASET OVERVIEW
# =====================================================
overview_metrics = {

    "Rows":
        len(df),

    "Columns":
        len(df.columns),

    "Missing Values":
        int(df.isnull().sum().sum()),

    "Duplicate Rows":
        int(df.duplicated().sum()),

    "Memory Usage MB":
        round(
            df.memory_usage(
                deep=True
            ).sum() / 1024 / 1024,
            2
        )
}

sections.append({

    "title": "Dataset Overview",

    "kv": overview_metrics
})

# =====================================================
# SECTION 2 — DATASET STATISTICS
# =====================================================
try:

    stats_df = df.describe(
        include="all"
    ).reset_index()

    sections.append({

        "title": "Dataset Statistics",

        "df": stats_df
    })

except:
    pass

# =====================================================
# SECTION 3 — AI ANALYSIS SUMMARY
# =====================================================
summary_metrics = {}

# ---------------------------------------------
# FORECAST METRICS
# ---------------------------------------------
if "forecast_metrics" in report_data:

    for k, v in report_data[
        "forecast_metrics"
    ].items():

        summary_metrics[
            f"Forecast - {k}"
        ] = v

# ---------------------------------------------
# CHURN METRICS
# ---------------------------------------------
if "churn_metrics" in report_data:

    for k, v in report_data[
        "churn_metrics"
    ].items():

        summary_metrics[
            f"Churn - {k}"
        ] = v

# ---------------------------------------------
# MODEL COMPARISON
# ---------------------------------------------
if "model_comparison" in report_data:

    try:

        model_df = report_data[
            "model_comparison"
        ]

        if isinstance(
            model_df,
            pd.DataFrame
        ):

            best_model = model_df.head(1)

            summary_metrics[
                "Best Model"
            ] = str(
                best_model.iloc[0, 0]
            )

    except:
        pass

# ---------------------------------------------
# SEGMENTATION
# ---------------------------------------------
if "segments_summary" in report_data:

    try:

        seg_df = report_data[
            "segments_summary"
        ]

        summary_metrics[
            "Segments Found"
        ] = len(seg_df)

    except:
        pass

# ---------------------------------------------
# ADD SUMMARY SECTION
# ---------------------------------------------
if len(summary_metrics) > 0:

    sections.append({

        "title": "AI Analysis Summary",

        "kv": summary_metrics
    })

# =====================================================
# SUCCESS MESSAGE
# =====================================================
st.success(
    f"✅ {len(sections)} report sections ready."
)

# =====================================================
# SECTION PREVIEW
# =====================================================
for sec in sections:

    with st.expander(
        sec["title"]
    ):

        # -----------------------------------------
        # KEY VALUE TABLE
        # -----------------------------------------
        if "kv" in sec:

            kv_df = pd.DataFrame({

                "Metric":
                    list(sec["kv"].keys()),

                "Value":
                    list(sec["kv"].values())
            })

            st.dataframe(
                kv_df,
                use_container_width=True
            )

        # -----------------------------------------
        # DATAFRAME
        # -----------------------------------------
        if "df" in sec:

            st.dataframe(
                sec["df"].head(20),
                use_container_width=True
            )

# =====================================================
# EXPORT SECTION
# =====================================================
st.divider()

col1, col2 = st.columns(2)

# =====================================================
# EXCEL REPORT
# =====================================================
with col1:

    st.subheader(
        "📊 Excel Report"
    )

    sheets = {}

    for sec in sections:

        try:

            # -----------------------------
            # DATAFRAME SHEETS
            # -----------------------------
            if "df" in sec:

                sheets[
                    sec["title"][:31]
                ] = sec["df"]

            # -----------------------------
            # KV SHEETS
            # -----------------------------
            elif "kv" in sec:

                sheets[
                    sec["title"][:31]
                ] = pd.DataFrame({

                    "Metric":
                        list(sec["kv"].keys()),

                    "Value":
                        list(sec["kv"].values())
                })

        except:
            pass

    excel_bytes = to_excel_bytes(
        sheets
    )

    st.download_button(

        label="⬇️ Download Excel Report",

        data=excel_bytes,

        file_name=f"""

AI_BI_Report_{
datetime.date.today()
}.xlsx
        """.replace(
            "\n",
            ""
        ),

        mime="""
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        """.replace(
            "\n",
            ""
        ),

        type="primary"
    )

# =====================================================
# PDF REPORT
# =====================================================
with col2:

    st.subheader(
        "📄 PDF Report"
    )

    try:

        pdf_bytes = to_pdf_bytes(
            sections
        )

        st.download_button(

            label="⬇️ Download PDF Report",

            data=pdf_bytes,

            file_name=f"""

AI_BI_Report_{
datetime.date.today()
}.pdf
            """.replace(
                "\n",
                ""
            ),

            mime="application/pdf",

            type="primary"
        )

    except Exception as e:

        st.error(
            f"PDF export failed: {e}"
        )