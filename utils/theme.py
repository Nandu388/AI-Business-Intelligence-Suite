import streamlit as st

def apply_theme():

    st.markdown("""
    <style>

    /* =====================================================
    IMPORT FONT
    ===================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* =====================================================
    GLOBAL
    ===================================================== */

    * {
        font-family: 'Inter', sans-serif;
    }

    html, body, [class*="css"] {

        color: #E2E8F0;

        scroll-behavior: smooth;
    }

    /* =====================================================
    MAIN APP
    ===================================================== */

    .stApp {

        background:
            linear-gradient(
                135deg,
                #050816 0%,
                #0B1120 45%,
                #1E1B4B 100%
            );

        color: #E2E8F0;

        overflow-x: hidden;
    }

    /* =====================================================
    ANIMATED GLOW
    ===================================================== */

    .stApp::before {

        content: "";

        position: fixed;

        width: 650px;
        height: 650px;

        background:
            radial-gradient(
                circle,
                rgba(139,92,246,0.20),
                transparent 70%
            );

        top: -200px;
        right: -150px;

        z-index: 0;

        animation:
            pulseGlow 8s infinite ease-in-out;
    }

    @keyframes pulseGlow {

        0% {

            transform: scale(1);

            opacity: 0.6;
        }

        50% {

            transform: scale(1.12);

            opacity: 1;
        }

        100% {

            transform: scale(1);

            opacity: 0.6;
        }
    }

    /* =====================================================
    FADE UP
    ===================================================== */

    @keyframes fadeUp {

        from {

            opacity: 0;

            transform:
                translateY(25px);
        }

        to {

            opacity: 1;

            transform:
                translateY(0);
        }
    }

    /* =====================================================
    SIDEBAR
    ===================================================== */

    [data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #060B1A 0%,
                #0F172A 100%
            );

        border-right:
            1px solid rgba(255,255,255,0.06);
    }

    /* =====================================================
    SIDEBAR NAV
    ===================================================== */

    [data-testid="stSidebarNav"] {

        padding-top: 1rem;
    }

    [data-testid="stSidebarNav"] a {

        border-radius: 14px;

        margin-bottom: 12px;

        padding: 10px 14px;

        transition: all 0.3s ease;

        color: #E2E8F0 !important;

        font-weight: 500;

        animation: fadeUp 0.5s ease;
    }

    [data-testid="stSidebarNav"] a:hover {

        background:
            linear-gradient(
                135deg,
                #8B5CF6,
                #06B6D4
            );

        transform:
            translateX(6px);

        box-shadow:
            0 8px 24px rgba(139,92,246,0.35);

        color: white !important;
    }

    /* =====================================================
    ACTIVE PAGE
    ===================================================== */

    [data-testid="stSidebarNav"] a[aria-current="page"] {

        background:
            linear-gradient(
                135deg,
                #8B5CF6,
                #6366F1
            );

        color: white !important;

        font-weight: 700;

        box-shadow:
            0 8px 28px rgba(99,102,241,0.35);
    }

    /* =====================================================
    HEADERS
    ===================================================== */

    h1 {

        color: white;

        font-size: 2.8rem !important;

        font-weight: 800 !important;

        animation: fadeUp 0.8s ease;
    }

    h2, h3, h4 {

        color: #F8FAFC;

        animation: fadeUp 0.8s ease;
    }

    /* =====================================================
    TEXT
    ===================================================== */

    p, label {

        color: #CBD5E1;
    }

    /* =====================================================
    METRICS
    ===================================================== */

    [data-testid="metric-container"] {

        background:
            rgba(17,24,39,0.65);

        border:
            1px solid rgba(255,255,255,0.06);

        border-radius: 18px;

        padding: 18px;

        backdrop-filter: blur(14px);

        box-shadow:
            0 8px 24px rgba(0,0,0,0.25);

        transition: 0.3s;

        animation: fadeUp 0.7s ease;
    }

    [data-testid="metric-container"]:hover {

        transform:
            translateY(-5px);

        border:
            1px solid rgba(139,92,246,0.5);

        box-shadow:
            0 14px 34px rgba(139,92,246,0.25);
    }

    /* =====================================================
    BUTTONS
    ===================================================== */

    .stButton > button {

        background:
            linear-gradient(
                135deg,
                #8B5CF6,
                #06B6D4
            );

        color: white;

        border: none;

        border-radius: 14px;

        padding: 0.7rem 1.5rem;

        font-weight: 700;

        transition: all 0.3s ease;

        box-shadow:
            0 6px 18px rgba(139,92,246,0.25);
    }

    .stButton > button:hover {

        transform:
            scale(1.05);

        box-shadow:
            0 12px 28px rgba(139,92,246,0.45);
    }

    /* =====================================================
    INPUTS
    ===================================================== */

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox div,
    .stMultiSelect div {

        background:
            rgba(17,24,39,0.7) !important;

        color: white !important;

        border-radius: 14px !important;

        border:
            1px solid rgba(255,255,255,0.08) !important;
    }

    /* =====================================================
    SLIDER
    ===================================================== */

    .stSlider {

        animation: fadeUp 0.7s ease;
    }

    /* =====================================================
    DATAFRAMES
    ===================================================== */

    .stDataFrame {

        border-radius: 18px;

        overflow: hidden;

        border:
            1px solid rgba(255,255,255,0.06);

        animation: fadeUp 0.8s ease;
    }

    /* =====================================================
    TABS
    ===================================================== */

    [data-baseweb="tab-list"] {

        gap: 12px;
    }

    [data-baseweb="tab"] {

        background:
            rgba(17,24,39,0.6);

        border-radius: 14px;

        padding: 12px 18px;

        border:
            1px solid rgba(255,255,255,0.06);

        transition: 0.3s;

        color: #CBD5E1;
    }

    [data-baseweb="tab"]:hover {

        transform:
            translateY(-3px);

        background:
            linear-gradient(
                135deg,
                rgba(139,92,246,0.35),
                rgba(6,182,212,0.25)
            );
    }

    [aria-selected="true"] {

        background:
            linear-gradient(
                135deg,
                #8B5CF6,
                #06B6D4
            ) !important;

        color: white !important;

        font-weight: 700 !important;
    }

    /* =====================================================
    GRAPH CARDS
    ===================================================== */

    .graph-card {

        animation:
            graphFade 0.8s ease;

        border-radius: 22px;

        padding: 12px;

        background:
            rgba(17,24,39,0.45);

        backdrop-filter: blur(12px);

        border:
            1px solid rgba(255,255,255,0.06);

        margin-bottom: 20px;

        transition: 0.3s;
    }

    .graph-card:hover {

        transform:
            translateY(-6px);

        box-shadow:
            0 14px 34px rgba(139,92,246,0.25);

        border:
            1px solid rgba(139,92,246,0.35);
    }

    @keyframes graphFade {

        from {

            opacity: 0;

            transform:
                translateY(25px)
                scale(0.97);
        }

        to {

            opacity: 1;

            transform:
                translateY(0)
                scale(1);
        }
    }

    /* =====================================================
    ALERTS
    ===================================================== */

    .stAlert {

        border-radius: 18px;

        animation: fadeUp 0.7s ease;
    }

    /* =====================================================
    SCROLLBAR
    ===================================================== */

    ::-webkit-scrollbar {

        width: 10px;
    }

    ::-webkit-scrollbar-thumb {

        background:
            linear-gradient(
                #8B5CF6,
                #06B6D4
            );

        border-radius: 20px;
    }

    /* =====================================================
    PLOTLY
    ===================================================== */

    .js-plotly-plot {

        animation:
            graphFade 0.9s ease;
    }

    </style>
    """, unsafe_allow_html=True)