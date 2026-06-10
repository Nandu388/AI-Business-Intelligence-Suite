import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

from sklearn.preprocessing import LabelEncoder

from utils.session_state import init_session

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Business Insights",
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
    background: linear-gradient(135deg,#1E1E2F,#262B44);
    border: 1px solid #333;
    padding: 15px;
    border-radius: 15px;
}

div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# INIT SESSION
# =====================================================
init_session()

st.title("💡 Business Insights Dashboard")

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
        "Please upload dataset first."
    )

    st.stop()

# =====================================================
# REMOVE DUPLICATE COLUMNS
# =====================================================
df = df.loc[:, ~df.columns.duplicated()]

# =====================================================
# HANDLE DATE COLUMNS
# =====================================================
for col in df.columns:

    try:

        if (
            "date" in col.lower()
            or
            "time" in col.lower()
        ):

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    except:
        pass

# =====================================================
# ENCODE OBJECT COLUMNS
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
# COLUMN TYPES
# =====================================================
num_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

cat_cols = df.select_dtypes(
    exclude=np.number
).columns.tolist()

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("🔍 Dashboard Filters")

filtered_df = df.copy()

# -----------------------------------------------------
# NUMERIC FILTERS
# -----------------------------------------------------
for col in num_cols[:4]:

    try:

        min_v = float(df[col].min())
        max_v = float(df[col].max())

        if min_v != max_v:

            selected = st.sidebar.slider(

                col,

                min_v,
                max_v,

                (min_v, max_v)
            )

            filtered_df = filtered_df[

                (filtered_df[col] >= selected[0])

                &

                (filtered_df[col] <= selected[1])
            ]

    except:
        pass

# -----------------------------------------------------
# CATEGORICAL FILTERS
# -----------------------------------------------------
for col in cat_cols[:3]:

    try:

        options = df[col].dropna().unique().tolist()

        selected = st.sidebar.multiselect(

            col,

            options,

            default=options
        )

        if selected:

            filtered_df = filtered_df[
                filtered_df[col].isin(selected)
            ]

    except:
        pass

# =====================================================
# KPI ROW
# =====================================================
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Records",
    len(filtered_df)
)

c2.metric(
    "Columns",
    len(filtered_df.columns)
)

if len(num_cols) > 0:

    c3.metric(
        "Numeric Columns",
        len(num_cols)
    )

if len(cat_cols) > 0:

    c4.metric(
        "Categorical Columns",
        len(cat_cols)
    )

# =====================================================
# MAIN DASHBOARD TABS
# =====================================================
tab1, tab2, tab3 = st.tabs([

    "📊 Executive Overview",

    "📈 Advanced Insights",

    "🛠️ Custom Analytics"
])

# =====================================================
# TAB 1
# =====================================================
with tab1:

    # -------------------------------------------------
    # ROW 1
    # -------------------------------------------------
    col1, col2 = st.columns(2)

    # =================================================
    # BAR CHART
    # =================================================
    with col1:

        st.subheader("📊 Category Analysis")

        if len(cat_cols) > 0 and len(num_cols) > 0:

            group_col = st.selectbox(
                "Category Column",
                cat_cols,
                key="group"
            )

            metric_col = st.selectbox(
                "Metric Column",
                num_cols,
                key="metric"
            )

            agg_type = st.selectbox(
                "Aggregation",
                [
                    "sum",
                    "mean",
                    "median",
                    "count"
                ]
            )

            try:

                grp = filtered_df.groupby(
                    group_col
                )[metric_col].agg(
                    agg_type
                ).reset_index()

                grp = grp.sort_values(
                    metric_col,
                    ascending=False
                ).head(10)

                fig = px.bar(

                    grp,

                    x=group_col,

                    y=metric_col,

                    color=metric_col,

                    title="Business Performance"
                )

                fig.update_layout(
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            except:

                st.info(
                    "Bar chart unavailable."
                )

    # =================================================
    # PIE CHART
    # =================================================
    with col2:

        st.subheader("🥧 Distribution")

        if len(cat_cols) > 0:

            try:

                pie_col = st.selectbox(
                    "Pie Column",
                    cat_cols,
                    key="pie"
                )

                vc = filtered_df[
                    pie_col
                ].value_counts().head(10)

                pie_fig = px.pie(

                    values=vc.values,

                    names=vc.index,

                    hole=0.4
                )

                pie_fig.update_layout(
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(
                    pie_fig,
                    use_container_width=True
                )

            except:

                st.info(
                    "Pie chart unavailable."
                )

    # -------------------------------------------------
    # ROW 2
    # -------------------------------------------------
    col3, col4 = st.columns(2)

    # =================================================
    # HISTOGRAM
    # =================================================
    with col3:

        st.subheader("📈 Distribution Analysis")

        if len(num_cols) > 0:

            try:

                hist_col = st.selectbox(
                    "Histogram Column",
                    num_cols,
                    key="hist"
                )

                hist_fig = px.histogram(

                    filtered_df,

                    x=hist_col,

                    nbins=30
                )

                hist_fig.update_layout(
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(
                    hist_fig,
                    use_container_width=True
                )

            except:

                st.info(
                    "Histogram unavailable."
                )

    # =================================================
    # CORRELATION HEATMAP
    # =================================================
    with col4:

        st.subheader("🔥 Correlation Heatmap")

        if len(num_cols) >= 2:

            try:

                corr = filtered_df[
                    num_cols
                ].corr()

                heatmap = px.imshow(

                    corr,

                    text_auto=True,

                    aspect="auto"
                )

                heatmap.update_layout(
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(
                    heatmap,
                    use_container_width=True
                )

            except:

                st.info(
                    "Heatmap unavailable."
                )

# =====================================================
# TAB 2
# =====================================================
with tab2:

    # -------------------------------------------------
    # TOP/BOTTOM
    # -------------------------------------------------
    col5, col6 = st.columns(2)

    with col5:

        st.subheader("🏆 Top Records")

        if len(num_cols) > 0:

            top_col = st.selectbox(
                "Top Column",
                num_cols,
                key="top"
            )

            top_df = filtered_df.nlargest(
                10,
                top_col
            )

            st.dataframe(
                top_df,
                use_container_width=True,
                height=400
            )

    with col6:

        st.subheader("📉 Bottom Records")

        if len(num_cols) > 0:

            bottom_col = st.selectbox(
                "Bottom Column",
                num_cols,
                key="bottom"
            )

            bottom_df = filtered_df.nsmallest(
                10,
                bottom_col
            )

            st.dataframe(
                bottom_df,
                use_container_width=True,
                height=400
            )

    # -------------------------------------------------
    # SCATTER
    # -------------------------------------------------
    st.subheader("🔍 Relationship Analysis")

    if len(num_cols) >= 2:

        c7, c8 = st.columns(2)

        x_col = c7.selectbox(
            "X Axis",
            num_cols,
            key="x"
        )

        y_col = c8.selectbox(
            "Y Axis",
            num_cols,
            key="y"
        )

        try:

            scatter_fig = px.scatter(

                filtered_df,

                x=x_col,

                y=y_col,

                color=y_col,

                size=y_col,

                hover_data=filtered_df.columns
            )

            scatter_fig.update_layout(
                template="plotly_dark",
                height=600
            )

            st.plotly_chart(
                scatter_fig,
                use_container_width=True
            )

        except:

            st.info(
                "Scatter plot unavailable."
            )

# =====================================================
# TAB 3
# =====================================================
with tab3:

    st.subheader("🛠️ Build Your Own Chart")

    chart_type = st.selectbox(

        "Chart Type",

        [
            "Bar",
            "Line",
            "Scatter",
            "Histogram",
            "Box",
            "Area"
        ]
    )

    x_axis = st.selectbox(
        "X Axis",
        filtered_df.columns
    )

    y_axis = st.selectbox(
        "Y Axis",
        num_cols
    )

    try:

        if chart_type == "Bar":

            custom_fig = px.bar(
                filtered_df,
                x=x_axis,
                y=y_axis
            )

        elif chart_type == "Line":

            custom_fig = px.line(
                filtered_df,
                x=x_axis,
                y=y_axis
            )

        elif chart_type == "Scatter":

            custom_fig = px.scatter(
                filtered_df,
                x=x_axis,
                y=y_axis
            )

        elif chart_type == "Histogram":

            custom_fig = px.histogram(
                filtered_df,
                x=x_axis
            )

        elif chart_type == "Box":

            custom_fig = px.box(
                filtered_df,
                x=x_axis,
                y=y_axis
            )

        elif chart_type == "Area":

            custom_fig = px.area(
                filtered_df,
                x=x_axis,
                y=y_axis
            )

        custom_fig.update_layout(
            template="plotly_dark",
            height=650
        )

        st.plotly_chart(
            custom_fig,
            use_container_width=True
        )

    except:

        st.warning(
            "Chart cannot be generated."
        )

# =====================================================
# DOWNLOAD
# =====================================================
st.download_button(

    "⬇️ Download Filtered Dataset",

    filtered_df.to_csv(index=False),

    "filtered_dataset.csv",

    "text/csv"
)