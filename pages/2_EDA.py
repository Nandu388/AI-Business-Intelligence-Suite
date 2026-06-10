import streamlit as st
import pandas as pd
import numpy as np

from utils.session_state import init_session

from utils.visualizer import (
    histogram,
    correlation_heatmap,
    scatter,
    pie_chart,
    bar,
    boxplot
)

import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="EDA Dashboard",
    layout="wide"
)

# =====================================================
# INIT SESSION
# =====================================================
init_session()

st.title("📊 Exploratory Data Analysis")

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
# COLUMN TYPES
# =====================================================
num_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

cat_cols = df.select_dtypes(
    exclude=np.number
).columns.tolist()

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([

    "📈 Distributions",

    "🔗 Correlations",

    "🔀 Bivariate",

    "🗂️ Categorical",

    "📐 Advanced Stats"
])

# =====================================================
# TAB 1 — DISTRIBUTIONS
# =====================================================
with tab1:

    st.subheader("Distribution Analysis")

    if len(num_cols) > 0:

        col = st.selectbox(
            "Select Numeric Column",
            num_cols,
            key="numeric_column_select"
        )

        c1, c2 = st.columns(2)

        # ---------------------------------------------
        # HISTOGRAM
        # ---------------------------------------------
        with c1:

            st.plotly_chart(
                histogram(df, col),
                use_container_width=True
            )

        # ---------------------------------------------
        # BOXPLOT
        # ---------------------------------------------
        with c2:

            st.plotly_chart(
                boxplot(df, col),
                use_container_width=True
            )

        # ---------------------------------------------
        # VIOLIN PLOTS
        # ---------------------------------------------
        st.subheader("Violin Plot Comparison")

        selected = st.multiselect(
            "Select Columns",
            num_cols,
            default=num_cols[:4],
            key="violin_plot_columns"
        )

        if len(selected) > 0:

            fig = go.Figure()

            colors = [
                "#B39DDB",
                "#80CBC4",
                "#FFAB91",
                "#F48FB1",
                "#AED581"
            ]

            for i, c in enumerate(selected):

                fig.add_trace(

                    go.Violin(

                        y=df[c],

                        name=c,

                        fillcolor=colors[
                            i % len(colors)
                        ],

                        line_color=colors[
                            i % len(colors)
                        ],

                        opacity=0.7
                    )
                )

            fig.update_layout(
                title="Violin Plot Comparison",
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.warning(
            "No numeric columns available."
        )

# =====================================================
# TAB 2 — CORRELATIONS
# =====================================================
with tab2:

    st.subheader("Correlation Matrix")

    if len(num_cols) > 1:

        st.plotly_chart(
            correlation_heatmap(df),
            use_container_width=True
        )

        threshold = st.slider(
            "Correlation Threshold",
            0.1,
            1.0,
            0.5,
            key="corr_threshold"
        )

        corr = df[num_cols].corr().abs()

        strong = corr[
            (corr > threshold)
            & (corr < 1.0)
        ].stack().reset_index()

        strong.columns = [
            "Column A",
            "Column B",
            "Correlation"
        ]

        strong = strong.drop_duplicates()

        st.subheader("Strong Correlations")

        st.dataframe(
            strong.sort_values(
                "Correlation",
                ascending=False
            ),
            use_container_width=True
        )

    else:

        st.warning(
            "Need at least 2 numeric columns."
        )

# =====================================================
# TAB 3 — BIVARIATE ANALYSIS
# =====================================================
with tab3:

    st.subheader("Scatter Plot")

    if len(num_cols) >= 2:

        c1, c2 = st.columns(2)

        x_col = c1.selectbox(
            "X Axis",
            num_cols,
            index=0,
            key="x_axis"
        )

        y_col = c2.selectbox(
            "Y Axis",
            num_cols,
            index=1,
            key="y_axis"
        )

        color_col = st.selectbox(
            "Color By",
            ["None"] + cat_cols + num_cols,
            key="color_by"
        )

        color = (
            None
            if color_col == "None"
            else color_col
        )

        st.plotly_chart(
            scatter(
                df,
                x_col,
                y_col,
                color
            ),
            use_container_width=True
        )

    else:

        st.warning(
            "Need at least 2 numeric columns."
        )

# =====================================================
# TAB 4 — CATEGORICAL
# =====================================================
with tab4:

    st.subheader("Categorical Analysis")

    if len(cat_cols) > 0:

        col = st.selectbox(
            "Select Category Column",
            cat_cols,
            key="category_column"
        )

        vc = df[col].value_counts().head(20)

        c1, c2 = st.columns(2)

        # ---------------------------------------------
        # BAR CHART
        # ---------------------------------------------
        with c1:

            chart_df = pd.DataFrame({

                "Category": vc.index,

                "Count": vc.values
            })

            st.plotly_chart(

                bar(
                    chart_df,
                    "Category",
                    "Count",
                    f"Top Values in {col}"
                ),

                use_container_width=True
            )

        # ---------------------------------------------
        # PIE CHART
        # ---------------------------------------------
        with c2:

            st.plotly_chart(

                pie_chart(
                    vc.index.tolist(),
                    vc.values.tolist(),
                    f"{col} Distribution"
                ),

                use_container_width=True
            )

    else:

        st.info(
            "No categorical columns detected."
        )

# =====================================================
# TAB 5 — ADVANCED STATS
# =====================================================
with tab5:

    st.subheader("Advanced Statistics")

    if len(num_cols) > 0:

        stats_df = pd.DataFrame({

            "Skewness":
                df[num_cols].skew().round(3),

            "Kurtosis":
                df[num_cols].kurt().round(3),

            "Mean":
                df[num_cols].mean().round(3),

            "Median":
                df[num_cols].median().round(3),

            "Std Dev":
                df[num_cols].std().round(3),

            "CV %":
                (
                    df[num_cols].std()
                    / df[num_cols].mean()
                    * 100
                ).round(2)
        })

        st.dataframe(
            stats_df,
            use_container_width=True
        )

        # ---------------------------------------------
        # SCATTER MATRIX
        # ---------------------------------------------
        st.subheader("Scatter Matrix")

        selected_pp = st.multiselect(
            "Select Columns for Scatter Matrix",
            num_cols,
            default=num_cols[:4],
            key="scatter_matrix_columns"
        )

        if len(selected_pp) >= 2:

            sample_size = min(
                500,
                len(df)
            )

            fig = px.scatter_matrix(

                df[selected_pp].sample(
                    sample_size
                ),

                color_discrete_sequence=[
                    "#B39DDB"
                ]
            )

            fig.update_layout(
                template="plotly_dark",
                height=700
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.warning(
            "No numeric columns available."
        )