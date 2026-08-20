import os
import base64
import streamlit as st


# ============================================================
# IMAGE HELPER
# ============================================================

def get_base64_image(image_path):
    """
    Convert image into base64 for CSS background usage.
    """

    if not image_path:
        return None

    if not os.path.exists(image_path):
        return None

    try:

        with open(
            image_path,
            "rb"
        ) as image_file:

            return base64.b64encode(
                image_file.read()
            ).decode(
                "utf-8"
            )

    except Exception:

        return None


# ============================================================
# GLOBAL AUTHENTICATED APPLICATION THEME
# ============================================================

def apply_global_theme(
    image_path=None
):
    """
    Apply authenticated RetailPulse AI dashboard theme.

    If dashboard background image exists, it is used behind
    Dashboard, Analytics, Forecasting, Business Insights
    and Dataset Information pages.
    """

    encoded_image = get_base64_image(
        image_path
    )


    # ========================================================
    # DASHBOARD BACKGROUND
    # ========================================================

    if encoded_image:

        background_css = f"""
        background-image:
            linear-gradient(
                rgba(3, 10, 22, 0.88),
                rgba(3, 10, 22, 0.90)
            ),
            url("data:image/png;base64,{encoded_image}");

        background-size:
            cover;

        background-position:
            center center;

        background-repeat:
            no-repeat;

        background-attachment:
            fixed;
        """

    else:

        background_css = """
        background:
            linear-gradient(
                135deg,
                #07111f 0%,
                #0b1728 45%,
                #0d1b2e 100%
            );
        """


    # ========================================================
    # GLOBAL CSS
    # ========================================================

    css = f"""
    <style>

    /* =====================================================
       APPLICATION BACKGROUND
    ===================================================== */

    html,
    body {{
        background:
            #06111f !important;
    }}


    .stApp {{
        {background_css}

        color:
            #e2e8f0 !important;

        min-height:
            100vh;
    }}


    [data-testid="stAppViewContainer"] {{
        background:
            transparent !important;
    }}


    [data-testid="stMain"] {{
        background:
            transparent !important;
    }}


    /* =====================================================
       HEADER
    ===================================================== */

    header[data-testid="stHeader"] {{
        background:
            rgba(
                3,
                10,
                22,
                0.55
            ) !important;

        backdrop-filter:
            blur(16px);

        border-bottom:
            1px solid
            rgba(
                148,
                163,
                184,
                0.08
            );
    }}


    /* =====================================================
       MAIN CONTENT
    ===================================================== */

    .block-container {{
        padding-top:
            2rem !important;

        padding-bottom:
            3rem !important;

        max-width:
            1500px !important;
    }}


    /* =====================================================
       HEADINGS
    ===================================================== */

    h1 {{
        color:
            #f8fafc !important;

        font-weight:
            800 !important;

        letter-spacing:
            -0.02em;

        text-shadow:
            0 2px 12px
            rgba(
                0,
                0,
                0,
                0.35
            );
    }}


    h2,
    h3,
    h4 {{
        color:
            #f1f5f9 !important;
    }}


    /* =====================================================
       NORMAL TEXT
    ===================================================== */

    p,
    label {{
        color:
            #cbd5e1;
    }}


    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {{
        display:
            block !important;

        background:
            linear-gradient(
                180deg,
                rgba(4, 12, 25, 0.98) 0%,
                rgba(7, 20, 38, 0.97) 100%
            ) !important;

        border-right:
            1px solid
            rgba(
                96,
                165,
                250,
                0.12
            );

        backdrop-filter:
            blur(16px);
    }}


    section[data-testid="stSidebar"] > div {{
        background:
            transparent !important;
    }}


    /* =====================================================
       SIDEBAR RADIO NAVIGATION
    ===================================================== */

    div[role="radiogroup"] label {{
        padding:
            9px 9px;

        border-radius:
            9px;

        transition:
            all 0.20s ease;
    }}


    div[role="radiogroup"] label:hover {{
        background:
            rgba(
                59,
                130,
                246,
                0.12
            );
    }}


    /* =====================================================
       METRIC CARDS
    ===================================================== */

    div[data-testid="stMetric"] {{
        background:
            linear-gradient(
                145deg,
                rgba(10, 24, 45, 0.82),
                rgba(8, 18, 34, 0.76)
            );

        border:
            1px solid
            rgba(
                96,
                165,
                250,
                0.15
            );

        padding:
            18px;

        border-radius:
            15px;

        box-shadow:
            0 12px 35px
            rgba(
                0,
                0,
                0,
                0.25
            );

        backdrop-filter:
            blur(14px);
    }}


    div[data-testid="stMetricLabel"] {{
        color:
            #94a3b8 !important;
    }}


    div[data-testid="stMetricValue"] {{
        color:
            #f8fafc !important;
    }}


    div[data-testid="stMetricDelta"] {{
        color:
            #7dd3fc !important;
    }}


    /* =====================================================
       BORDERED CONTAINERS
    ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:
            linear-gradient(
                145deg,
                rgba(7, 18, 34, 0.80),
                rgba(10, 26, 47, 0.73)
            ) !important;

        border:
            1px solid
            rgba(
                96,
                165,
                250,
                0.14
            ) !important;

        border-radius:
            16px !important;

        box-shadow:
            0 12px 35px
            rgba(
                0,
                0,
                0,
                0.22
            );

        backdrop-filter:
            blur(16px);
    }}


    /* =====================================================
       DATAFRAME
    ===================================================== */

    div[data-testid="stDataFrame"] {{
        border-radius:
            12px;

        overflow:
            hidden;

        border:
            1px solid
            rgba(
                96,
                165,
                250,
                0.12
            );

        background:
            rgba(
                5,
                15,
                30,
                0.82
            );
    }}


    /* =====================================================
       INPUTS
    ===================================================== */

    div[data-testid="stTextInput"]
    div[data-baseweb="input"] {{
        background:
            rgba(
                8,
                20,
                38,
                0.88
            ) !important;

        border:
            1px solid
            rgba(
                148,
                163,
                184,
                0.18
            ) !important;

        border-radius:
            10px !important;
    }}


    div[data-testid="stTextInput"] input {{
        color:
            #f8fafc !important;

        background:
            transparent !important;
    }}


    div[data-testid="stTextInput"]
    input::placeholder {{
        color:
            #64748b !important;
    }}


    /* =====================================================
       SELECTBOX
    ===================================================== */

    div[data-baseweb="select"] > div {{
        background:
            rgba(
                8,
                20,
                38,
                0.88
            ) !important;

        border-color:
            rgba(
                148,
                163,
                184,
                0.18
            ) !important;

        border-radius:
            10px !important;
    }}


    /* =====================================================
       BUTTONS
    ===================================================== */

    div[data-testid="stButton"] button {{
        min-height:
            44px;

        border-radius:
            10px !important;

        font-weight:
            700 !important;

        transition:
            all 0.20s ease;
    }}


    div[data-testid="stButton"] button:hover {{
        transform:
            translateY(-1px);

        border-color:
            #60a5fa !important;
    }}


    div[data-testid="stButton"]
    button[kind="primary"] {{
        background:
            linear-gradient(
                90deg,
                #2563eb,
                #4f46e5
            ) !important;

        color:
            white !important;

        border:
            none !important;
    }}


    div[data-testid="stButton"]
    button[kind="primary"]:hover {{
        background:
            linear-gradient(
                90deg,
                #3b82f6,
                #6366f1
            ) !important;
    }}


    /* =====================================================
       FILE UPLOADER
    ===================================================== */

    section[data-testid="stFileUploaderDropzone"] {{
        background:
            rgba(
                8,
                20,
                38,
                0.75
            ) !important;

        border:
            1px dashed
            rgba(
                96,
                165,
                250,
                0.35
            ) !important;

        border-radius:
            14px;
    }}


    /* =====================================================
       EXPANDERS
    ===================================================== */

    details {{
        background:
            rgba(
                7,
                18,
                34,
                0.70
            );

        border-radius:
            12px;

        border:
            1px solid
            rgba(
                148,
                163,
                184,
                0.10
            );
    }}


    /* =====================================================
       TABS
    ===================================================== */

    button[data-baseweb="tab"] {{
        color:
            #cbd5e1 !important;

        font-weight:
            650 !important;
    }}


    /* =====================================================
       ALERTS
    ===================================================== */

    div[data-testid="stAlert"] {{
        border-radius:
            11px !important;

        backdrop-filter:
            blur(12px);
    }}


    /* =====================================================
       CAPTIONS
    ===================================================== */

    [data-testid="stCaptionContainer"] {{
        color:
            #94a3b8 !important;
    }}


    /* =====================================================
       DIVIDERS
    ===================================================== */

    hr {{
        border-color:
            rgba(
                148,
                163,
                184,
                0.12
            ) !important;
    }}


    /* =====================================================
       PROGRESS BAR
    ===================================================== */

    div[data-testid="stProgress"] {{
        border-radius:
            10px;
    }}


    /* =====================================================
       DOWNLOAD BUTTON
    ===================================================== */

    div[data-testid="stDownloadButton"] button {{
        border-radius:
            10px !important;

        font-weight:
            650 !important;
    }}


    /* =====================================================
       SCROLLBAR
    ===================================================== */

    ::-webkit-scrollbar {{
        width:
            8px;

        height:
            8px;
    }}


    ::-webkit-scrollbar-track {{
        background:
            #06111f;
    }}


    ::-webkit-scrollbar-thumb {{
        background:
            #334155;

        border-radius:
            10px;
    }}


    ::-webkit-scrollbar-thumb:hover {{
        background:
            #475569;
    }}


    /* =====================================================
       MOBILE
    ===================================================== */

    @media (max-width: 900px) {{

        .block-container {{
            padding-left:
                1rem !important;

            padding-right:
                1rem !important;
        }}
    }}

    </style>
    """


    st.markdown(
        css,
        unsafe_allow_html=True
    )


# ============================================================
# LOGIN BACKGROUND
# ============================================================

def apply_login_background(
    image_path=None
):
    """
    Apply login background and login-specific theme.
    """

    encoded_image = get_base64_image(
        image_path
    )


    # ========================================================
    # BACKGROUND
    # ========================================================

    if encoded_image:

        background_css = f"""
        background-image:
            linear-gradient(
                90deg,
                rgba(2, 10, 22, 0.72) 0%,
                rgba(2, 10, 22, 0.66) 40%,
                rgba(2, 10, 22, 0.82) 70%,
                rgba(2, 10, 22, 0.94) 100%
            ),
            url("data:image/png;base64,{encoded_image}");

        background-size:
            cover;

        background-position:
            center center;

        background-repeat:
            no-repeat;

        background-attachment:
            fixed;
        """

    else:

        background_css = """
        background:
            linear-gradient(
                135deg,
                #020817 0%,
                #071426 48%,
                #030914 100%
            );
        """


    # ========================================================
    # LOGIN CSS
    # ========================================================

    css = f"""
    <style>

    /* =====================================================
       LOGIN BACKGROUND
    ===================================================== */

    .stApp {{
        {background_css}

        min-height:
            100vh !important;
    }}


    [data-testid="stAppViewContainer"] {{
        background:
            transparent !important;
    }}


    [data-testid="stMain"] {{
        background:
            transparent !important;
    }}


    /* =====================================================
       HEADER
    ===================================================== */

    header[data-testid="stHeader"] {{
        background:
            transparent !important;
    }}


    /* =====================================================
       LOGIN CONTENT
    ===================================================== */

    .block-container {{
        max-width:
            1450px !important;

        padding-top:
            2rem !important;

        padding-bottom:
            2rem !important;
    }}


    /* =====================================================
       HIDE SIDEBAR BEFORE LOGIN
    ===================================================== */

    section[data-testid="stSidebar"] {{
        display:
            none !important;
    }}


    /* =====================================================
       HEADINGS
    ===================================================== */

    h1 {{
        color:
            #f8fafc !important;

        font-weight:
            800 !important;

        text-shadow:
            0 2px 14px
            rgba(
                0,
                0,
                0,
                0.35
            );
    }}


    h2,
    h3 {{
        color:
            #e2e8f0 !important;
    }}


    p {{
        color:
            #cbd5e1 !important;
    }}


    /* =====================================================
       CAPTION
    ===================================================== */

    [data-testid="stCaptionContainer"] {{
        color:
            #7dd3fc !important;

        font-weight:
            650 !important;

        letter-spacing:
            0.03em;
    }}


    /* =====================================================
       LOGIN / FEATURE CONTAINERS
    ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:
            rgba(
                7,
                15,
                28,
                0.76
            ) !important;

        border:
            1px solid
            rgba(
                148,
                163,
                184,
                0.18
            ) !important;

        border-radius:
            18px !important;

        box-shadow:
            0 15px 45px
            rgba(
                0,
                0,
                0,
                0.24
            );

        backdrop-filter:
            blur(14px);
    }}


    /* =====================================================
       INPUT LABELS
    ===================================================== */

    div[data-testid="stTextInput"] label {{
        color:
            #e2e8f0 !important;

        font-weight:
            600 !important;
    }}


    /* =====================================================
       INPUTS
    ===================================================== */

    div[data-testid="stTextInput"]
    div[data-baseweb="input"] {{
        background:
            rgba(
                15,
                23,
                42,
                0.86
            ) !important;

        border:
            1px solid
            rgba(
                148,
                163,
                184,
                0.22
            ) !important;

        border-radius:
            10px !important;
    }}


    div[data-testid="stTextInput"] input {{
        color:
            #f8fafc !important;

        background:
            transparent !important;
    }}


    div[data-testid="stTextInput"]
    input::placeholder {{
        color:
            #64748b !important;
    }}


    /* =====================================================
       BUTTONS
    ===================================================== */

    div[data-testid="stButton"] button {{
        min-height:
            45px;

        border-radius:
            10px !important;

        font-weight:
            700 !important;
    }}


    div[data-testid="stButton"]
    button[kind="primary"] {{
        background:
            linear-gradient(
                90deg,
                #2563eb,
                #4f46e5
            ) !important;

        color:
            white !important;

        border:
            none !important;
    }}


    div[data-testid="stButton"]
    button[kind="primary"]:hover {{
        background:
            linear-gradient(
                90deg,
                #3b82f6,
                #6366f1
            ) !important;
    }}


    /* =====================================================
       TABS
    ===================================================== */

    button[data-baseweb="tab"] {{
        color:
            #cbd5e1 !important;

        font-weight:
            650 !important;
    }}


    /* =====================================================
       ALERTS
    ===================================================== */

    div[data-testid="stAlert"] {{
        border-radius:
            10px !important;
    }}


    /* =====================================================
       MOBILE
    ===================================================== */

    @media (max-width: 900px) {{

        .block-container {{
            padding-left:
                1rem !important;

            padding-right:
                1rem !important;
        }}
    }}

    </style>
    """


    st.markdown(
        css,
        unsafe_allow_html=True
    )