import streamlit as st
import pandas as pd
import numpy as np
import os

from utils.preprocess import (
    load_data,
    basic_info,
    get_column_types,
    get_outlier_summary,
    preprocess_df
)

from utils.session_state import (
    init_session
)

from utils.visualizer import (
    boxplot
)

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI BI Suite",
    page_icon="📂",
    layout="wide"
)

# =========================================================
# INIT SESSION
# =========================================================
init_session()

# =========================================================
# CLEAN DARK THEME
# =========================================================
st.markdown("""
<style>

.stApp {

    background-color: #0F172A;

    color: white;
}

[data-testid="stSidebar"] {

    background-color: #111827;
}

h1, h2, h3 {

    color: white;
}

.stButton > button {

    background-color: #2563EB;

    color: white;

    border: none;

    border-radius: 8px;
}

[data-testid="metric-container"] {

    background-color: #1E293B;

    border-radius: 12px;

    padding: 12px;
}

.stDataFrame {

    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("📂 Data Upload & Preprocessing")

# =========================================================
# SAMPLE DATA FOLDER
# =========================================================
SAMPLE_FOLDER = "sample_data"

sample_files = {}

if os.path.exists(SAMPLE_FOLDER):

    for file in os.listdir(SAMPLE_FOLDER):

        if file.endswith(".csv"):

            display_name = (
                file
                .replace("_", " ")
                .replace(".csv", "")
                .title()
            )

            sample_files[display_name] = os.path.join(
                SAMPLE_FOLDER,
                file
            )

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.header("📊 Dataset Options")

    data_source = st.radio(

        "Choose Data Source",

        [
            "Upload Dataset",
            "Use Sample Dataset"
        ]
    )

# =========================================================
# RESET SESSION ON SOURCE CHANGE
# =========================================================
if "last_source" not in st.session_state:

    st.session_state.last_source = data_source

if st.session_state.last_source != data_source:

    st.session_state.df = None

    st.session_state.df_processed = None

    st.session_state.last_source = data_source

# =========================================================
# SAMPLE DATASET
# =========================================================
if data_source == "Use Sample Dataset":

    if len(sample_files) == 0:

        st.warning(
            "No sample datasets found."
        )

        st.stop()

    selected_dataset = st.sidebar.selectbox(

        "Select Dataset",

        ["-- Select Dataset --"] + list(sample_files.keys())
    )

    # =====================================================
    # WAIT FOR USER SELECTION
    # =====================================================
    if selected_dataset == "-- Select Dataset --":

        st.info(
            "👈 Please select a sample dataset."
        )

        st.stop()

    # =====================================================
    # LOAD DATASET
    # =====================================================
    try:

        df = pd.read_csv(
            sample_files[selected_dataset]
        )

        # clean column names
        df.columns = [
            str(c)
            for c in df.columns
        ]

        # remove duplicate columns
        df = df.loc[
            :,
            ~pd.Index(df.columns).duplicated()
        ]

        st.session_state.df = df

        st.success(
            f"✅ Loaded {selected_dataset}"
        )

    except Exception as e:

        st.error(
            f"Could not load dataset: {e}"
        )

        st.stop()

# =========================================================
# FILE UPLOAD
# =========================================================
else:

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel File",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is None:

        st.info(
            "👈 Upload a dataset first."
        )

        st.stop()

    try:

        df = load_data(uploaded_file)

        # clean column names
        df.columns = [
            str(c)
            for c in df.columns
        ]

        # remove duplicate columns
        df = df.loc[
            :,
            ~pd.Index(df.columns).duplicated()
        ]

        st.session_state.df = df

        st.success(
            f"✅ Loaded {uploaded_file.name}"
        )

    except Exception as e:

        st.error(
            f"File loading failed: {e}"
        )

        st.stop()

# =========================================================
# MAIN DATAFRAME
# =========================================================
df = st.session_state.get("df")

if df is None:

    st.warning(
        "Dataset not loaded."
    )

    st.stop()

# =========================================================
# CLEAN DATAFRAME
# =========================================================
try:

    df.columns = [
        str(c)
        for c in df.columns
    ]

    df = df.loc[
        :,
        ~pd.Index(df.columns).duplicated()
    ]

except:
    pass

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([

    "📊 Overview",

    "👀 Data Preview",

    "🧹 Preprocessing",

    "📈 Outliers"
])

# =========================================================
# TAB 1
# =========================================================
with tab1:

    try:

        info = basic_info(df)

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Rows",
            f"{info['rows']:,}"
        )

        c2.metric(
            "Columns",
            info["columns"]
        )

        c3.metric(
            "Missing %",
            info["missing_pct"]
        )

        c4.metric(
            "Duplicates",
            info["duplicates"]
        )

        c5.metric(
            "Memory MB",
            info["memory_mb"]
        )

    except Exception as e:

        st.warning(
            f"Could not calculate metrics: {e}"
        )

    st.markdown("---")

    st.subheader("📋 Column Summary")

    try:

        summary = pd.DataFrame({

            "Column":
                [str(c) for c in df.columns],

            "Data Type":
                [str(x) for x in df.dtypes],

            "Null Count":
                [
                    int(x)
                    for x in df.isnull().sum().values
                ],

            "Unique Values":
                [
                    int(x)
                    for x in df.nunique().values
                ]
        })

        summary = summary.reset_index(
            drop=True
        )

        st.dataframe(
            summary.astype(str),
            use_container_width=True
        )

    except Exception as e:

        st.warning(
            f"Could not display summary: {e}"
        )

    st.markdown("---")

    try:

        num_cols, cat_cols, dt_cols = (
            get_column_types(df)
        )

        c1, c2, c3 = st.columns(3)

        c1.info(
            f"Numeric Columns: {len(num_cols)}"
        )

        c2.info(
            f"Categorical Columns: {len(cat_cols)}"
        )

        c3.info(
            f"Datetime Columns: {len(dt_cols)}"
        )

    except Exception as e:

        st.warning(
            f"Could not detect column types: {e}"
        )

# =========================================================
# TAB 2
# =========================================================
with tab2:

    st.subheader("👀 Dataset Preview")

    rows = st.slider(
        "Rows to Preview",
        5,
        min(100, len(df)),
        20
    )

    try:

        preview_df = df.head(rows).copy()

        preview_df.columns = [
            str(c)
            for c in preview_df.columns
        ]

        st.dataframe(
            preview_df.astype(str),
            use_container_width=True
        )

    except Exception as e:

        st.warning(
            f"Could not render preview: {e}"
        )

    st.markdown("---")

    st.subheader("📈 Dataset Statistics")

    try:

        stats_df = (
            df.describe(include="all")
            .fillna("")
        )

        stats_df.columns = [
            str(c)
            for c in stats_df.columns
        ]

        st.dataframe(
            stats_df.astype(str),
            use_container_width=True
        )

    except Exception as e:

        st.warning(
            f"Statistics unavailable: {e}"
        )

# =========================================================
# TAB 3
# =========================================================
with tab3:

    st.subheader("🧹 Data Preprocessing")

    drop_thresh = st.slider(
        "Drop Columns if Missing % >",
        10,
        90,
        60
    )

    run_preprocess = st.button(
        "🚀 Run Preprocessing",
        type="primary"
    )

    if run_preprocess:

        try:

            processed_df = preprocess_df(
                df,
                drop_thresh=(
                    drop_thresh / 100
                )
            )

            processed_df.columns = [
                str(c)
                for c in processed_df.columns
            ]

            processed_df = processed_df.loc[
                :,
                ~pd.Index(
                    processed_df.columns
                ).duplicated()
            ]

            st.session_state.df_processed = (
                processed_df
            )

            st.success(
                "✅ Preprocessing completed successfully."
            )

            st.dataframe(
                processed_df.head(20).astype(str),
                use_container_width=True
            )

        except Exception as e:

            st.warning(
                f"Preprocessing failed: {e}"
            )

    if st.session_state.get(
        "df_processed"
    ) is not None:

        st.download_button(
            label="⬇️ Download Processed CSV",
            data=st.session_state[
                "df_processed"
            ].to_csv(index=False),
            file_name="processed.csv",
            mime="text/csv"
        )

# =========================================================
# TAB 4
# =========================================================
with tab4:

    st.subheader("📈 Outlier Detection")

    try:

        outliers = get_outlier_summary(df)

        if (
            outliers is not None
            and not outliers.empty
        ):

            outliers = outliers[
                outliers["Outliers"] > 0
            ]

            if len(outliers) > 0:

                st.dataframe(
                    outliers.astype(str),
                    use_container_width=True
                )

            else:

                st.success(
                    "✅ No major outliers found."
                )

        else:

            st.info(
                "No outlier information available."
            )

    except Exception as e:

        st.warning(
            f"Outlier detection failed: {e}"
        )

    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    if len(numeric_cols) > 0:

        selected_col = st.selectbox(
            "Select Numeric Column",
            numeric_cols
        )

        try:

            fig = boxplot(
                df,
                selected_col
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:

            st.warning(
                f"Could not generate boxplot: {e}"
            )

    else:

        st.info(
            "No numeric columns available."
        )