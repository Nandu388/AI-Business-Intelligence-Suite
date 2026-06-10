import streamlit as st
from utils.session_state import init_session

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI BI Suite",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# INIT SESSION
# =====================================================

init_session()

# =====================================================
# CLEAN CSS (NO ANIMATIONS)
# =====================================================

st.markdown("""
<style>

/* =====================================================
MAIN APP
===================================================== */

.stApp {

    background: linear-gradient(
        135deg,
        #0F172A 0%,
        #111827 50%,
        #1E1B4B 100%
    );

    color: #E2E8F0;

    overflow-x: hidden;
}

/* =====================================================
SIDEBAR
===================================================== */

[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #111827 0%,
        #0F172A 100%
    );

    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebarNav"] {

    padding-top: 1rem;
}

[data-testid="stSidebarNav"] a {

    border-radius: 12px;

    margin-bottom: 8px;
}

/* =====================================================
TITLE
===================================================== */

.main-title {

    font-size: 3.5rem;

    font-weight: 800;

    background: linear-gradient(
        90deg,
        #8B5CF6,
        #06B6D4
    );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}

.subtitle {

    color: #94A3B8;

    font-size: 1.2rem;

    margin-top: -10px;

    margin-bottom: 35px;
}

/* =====================================================
CARDS
===================================================== */

.metric-card {

    background: rgba(17,24,39,0.75);

    backdrop-filter: blur(14px);

    border-radius: 24px;

    padding: 1.7rem;

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35);

    height: 210px;
}

/* =====================================================
ICON
===================================================== */

.card-icon {

    font-size: 2.7rem;

    margin-bottom: 15px;
}

/* =====================================================
TITLE
===================================================== */

.card-title {

    font-size: 1.2rem;

    font-weight: 700;

    color: white;

    margin-bottom: 10px;
}

/* =====================================================
DESC
===================================================== */

.card-desc {

    color: #CBD5E1;

    font-size: 0.95rem;

    line-height: 1.6;
}

/* =====================================================
BUTTONS
===================================================== */

.stButton > button {

    background: linear-gradient(
        135deg,
        #8B5CF6,
        #06B6D4
    );

    color: white;

    border: none;

    border-radius: 12px;

    padding: 0.7rem 1.6rem;

    font-weight: 700;
}

/* =====================================================
METRICS
===================================================== */

[data-testid="metric-container"] {

    background: rgba(17,24,39,0.75);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 15px;

    box-shadow:
        0 6px 25px rgba(0,0,0,0.25);
}

/* =====================================================
INFO BOXES
===================================================== */

.stAlert {

    border-radius: 16px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class="main-title">
🧠 AI Business Intelligence Suite
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
Interactive AI Analytics Platform • Power BI Inspired • Enterprise Dashboard
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# FIRST ROW
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">📂</div>
        <div class="card-title">
            Data Upload
        </div>
        <div class="card-desc">
            Upload CSV and Excel datasets with automated preprocessing support.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">📊</div>
        <div class="card-title">
            Exploratory Analysis
        </div>
        <div class="card-desc">
            Discover trends, patterns, correlations, and hidden business insights.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">📈</div>
        <div class="card-title">
            Sales Forecasting
        </div>
        <div class="card-desc">
            Predict future sales using machine learning and AI forecasting models.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">🔮</div>
        <div class="card-title">
            Churn Prediction
        </div>
        <div class="card-desc">
            Identify customers likely to leave using intelligent AI classification.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# SECOND ROW
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)

with col5:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">👥</div>
        <div class="card-title">
            Customer Segmentation
        </div>
        <div class="card-desc">
            Build customer clusters using AI-driven segmentation techniques.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col6:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">⚙️</div>
        <div class="card-title">
            Model Training
        </div>
        <div class="card-desc">
            Train, validate, compare, and evaluate machine learning algorithms.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col7:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">💡</div>
        <div class="card-title">
            Business Insights
        </div>
        <div class="card-desc">
            Interactive analytics with advanced filtering and smart visualizations.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col8:

    st.markdown("""
    <div class="metric-card">
        <div class="card-icon">📄</div>
        <div class="card-title">
            Reports
        </div>
        <div class="card-desc">
            Export professional AI-generated Excel and PDF business reports.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# DATA STATUS
# =====================================================

st.markdown("<br><br>", unsafe_allow_html=True)

if st.session_state.get("df") is None:

    st.info(
        "👈 Please upload or select a dataset to begin analysis."
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<center style='color:#94A3B8;font-size:14px'>
AI BI Suite • Enterprise Analytics Platform • Machine Learning Powered
</center>
""", unsafe_allow_html=True)