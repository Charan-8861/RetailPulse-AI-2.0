import os
import streamlit as st

from utils.auth import (
    create_users_table,
    register_user,
    authenticate_user
)

from utils.ui_theme import (
    apply_global_theme,
    apply_login_background
)

from app_pages.dashboard import show_dashboard
from app_pages.data_upload import show_data_upload
from app_pages.analytics import show_analytics
from app_pages.forecasting_page import show_forecasting
from app_pages.business_insights_page import show_business_insights
from app_pages.dataset_info import show_dataset_info


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

MODELS_DIR = os.path.join(
    BASE_DIR,
    "models"
)

OUTPUTS_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

FORECASTS_DIR = os.path.join(
    OUTPUTS_DIR,
    "forecasts"
)

METRICS_DIR = os.path.join(
    OUTPUTS_DIR,
    "metrics"
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)


# ============================================================
# BACKGROUND IMAGES
# ============================================================

LOGIN_BACKGROUND = os.path.join(
    ASSETS_DIR,
    "login_bg.png"
)

DASHBOARD_BACKGROUND = os.path.join(
    ASSETS_DIR,
    "dashboard_bg.png"
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RetailPulse AI 2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# REQUIRED DIRECTORIES
# ============================================================

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)

os.makedirs(
    MODELS_DIR,
    exist_ok=True
)

os.makedirs(
    FORECASTS_DIR,
    exist_ok=True
)

os.makedirs(
    METRICS_DIR,
    exist_ok=True
)

os.makedirs(
    ASSETS_DIR,
    exist_ok=True
)


# ============================================================
# CREATE USER DATABASE
# ============================================================

create_users_table()


# ============================================================
# SESSION DEFAULTS
# ============================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "username" not in st.session_state:

    st.session_state.username = None


application_defaults = {

    "dataset_configured":
        False,

    "retail_df":
        None,

    "analysis_df":
        None,

    "current_file_name":
        None,

    "current_sheet_name":
        None,

    "date_column":
        None,

    "sales_column":
        None,

    "quantity_column":
        None,

    "product_column":
        None,

    "category_column":
        None,

    "region_column":
        None,

    "customer_column":
        None,

    "lstm_trained":
        False,

    "mae":
        None,

    "rmse":
        None,

    "mape":
        None,

    "r2":
        None,

    "comparison_df":
        None,

    "future_df":
        None,

    "loss_df":
        None,

    "combined_df":
        None,

    "model_comparison":
        None,

    "best_model":
        None,

    "best_mape":
        None,

    "percentage_change":
        None,

    "epochs_used":
        None,

    "forecast_frequency":
        None,

    "forecast_target_used":
        None
}


for key, value in application_defaults.items():

    if key not in st.session_state:

        st.session_state[
            key
        ] = value


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    # ========================================================
    # LOGIN BACKGROUND
    # ========================================================

    if os.path.exists(
        LOGIN_BACKGROUND
    ):

        apply_login_background(
            LOGIN_BACKGROUND
        )

    else:

        apply_login_background(
            None
        )

        st.warning(
            "Login background image was not found in "
            "`assets/login_bg.png`."
        )


    # ========================================================
    # LOGIN LAYOUT
    # ========================================================

    left_side, right_side = st.columns(
        [
            1.08,
            0.92
        ],
        gap="large"
    )


    # ========================================================
    # LEFT SIDE
    # ========================================================

    with left_side:

        st.write("")
        st.write("")

        st.caption(
            "AI-POWERED RETAIL INTELLIGENCE"
        )

        st.title(
            "📊 RetailPulse AI 2.0"
        )

        st.subheader(
            "Deep Learning-Powered "
            "Retail Decision Intelligence"
        )

        st.write(
            "Transform retail data into predictive intelligence "
            "using advanced analytics, LSTM demand forecasting "
            "and AI-driven business insights."
        )

        st.write("")


        feature_col1, feature_col2 = (
            st.columns(
                2,
                gap="medium"
            )
        )


        # ====================================================
        # FEATURE COLUMN 1
        # ====================================================

        with feature_col1:

            with st.container(
                border=True
            ):

                st.subheader(
                    "📈 Smart Analytics"
                )

                st.write(
                    "Explore sales trends, product performance, "
                    "regional activity and retail KPIs."
                )


            with st.container(
                border=True
            ):

                st.subheader(
                    "🧠 AI Forecasting"
                )

                st.write(
                    "Use LSTM-powered time-series forecasting "
                    "to estimate future retail demand."
                )


        # ====================================================
        # FEATURE COLUMN 2
        # ====================================================

        with feature_col2:

            with st.container(
                border=True
            ):

                st.subheader(
                    "🛡️ Business Health"
                )

                st.write(
                    "Monitor profitability, risks, loss-making "
                    "transactions and overall business health."
                )


            with st.container(
                border=True
            ):

                st.subheader(
                    "🎯 Profit Intelligence"
                )

                st.write(
                    "Receive data-driven recommendations for "
                    "pricing, discounts, products and operations."
                )


    # ========================================================
    # RIGHT SIDE
    # ========================================================

    with right_side:

        st.write("")
        st.write("")
        st.write("")

        st.title(
            "Welcome Back"
        )

        st.caption(
            "Sign in to your RetailPulse AI 2.0 account"
        )

        st.write("")


        # ====================================================
        # LOGIN CARD
        # ====================================================

        with st.container(
            border=True
        ):

            login_tab, register_tab = (
                st.tabs(
                    [
                        "🔐 Login",
                        "📝 Register"
                    ]
                )
            )


            # =================================================
            # LOGIN TAB
            # =================================================

            with login_tab:

                st.write("")

                login_username = (
                    st.text_input(
                        "Username",
                        placeholder="Enter your username",
                        key="login_username"
                    )
                )


                login_password = (
                    st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        key="login_password"
                    )
                )


                st.write("")


                if st.button(
                    "Sign In",
                    type="primary",
                    use_container_width=True,
                    key="login_button"
                ):

                    username_clean = (
                        login_username.strip()
                        if login_username
                        else ""
                    )


                    if (
                        not username_clean
                        or
                        not login_password
                    ):

                        st.warning(
                            "Please enter both username "
                            "and password."
                        )


                    else:

                        success, user = (
                            authenticate_user(
                                username_clean,
                                login_password
                            )
                        )


                        if success:

                            st.session_state.logged_in = (
                                True
                            )

                            st.session_state.username = (
                                user[1]
                            )

                            st.rerun()


                        else:

                            st.error(
                                "Invalid username or password."
                            )


            # =================================================
            # REGISTER TAB
            # =================================================

            with register_tab:

                st.write("")


                register_username = (
                    st.text_input(
                        "Choose Username",
                        placeholder="Create a username",
                        key="register_username"
                    )
                )


                register_password = (
                    st.text_input(
                        "Choose Password",
                        type="password",
                        placeholder="Create a password",
                        key="register_password"
                    )
                )


                confirm_password = (
                    st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Confirm your password",
                        key="confirm_password"
                    )
                )


                st.caption(
                    "Username should contain at least 3 characters. "
                    "Password should contain at least 6 characters."
                )


                st.write("")


                if st.button(
                    "Create Account",
                    use_container_width=True,
                    key="register_button"
                ):

                    username_clean = (
                        register_username.strip()
                        if register_username
                        else ""
                    )


                    if (
                        not username_clean
                        or
                        not register_password
                        or
                        not confirm_password
                    ):

                        st.warning(
                            "Please complete all registration fields."
                        )


                    elif len(
                        username_clean
                    ) < 3:

                        st.error(
                            "Username must contain at least "
                            "3 characters."
                        )


                    elif len(
                        register_password
                    ) < 6:

                        st.error(
                            "Password must contain at least "
                            "6 characters."
                        )


                    elif (
                        register_password
                        !=
                        confirm_password
                    ):

                        st.error(
                            "Passwords do not match."
                        )


                    else:

                        success, message = (
                            register_user(
                                username_clean,
                                register_password
                            )
                        )


                        if success:

                            st.success(
                                f"✅ {message}"
                            )

                            st.info(
                                "Your account is ready. "
                                "Open the Login tab to sign in."
                            )


                        else:

                            st.error(
                                message
                            )


            st.divider()

            st.caption(
                "🔒 Secure • Trusted • Intelligent"
            )


    # ========================================================
    # STOP BEFORE AUTHENTICATED APP
    # ========================================================

    st.stop()


# ============================================================
# AUTHENTICATED APPLICATION THEME
# ============================================================

if os.path.exists(
    DASHBOARD_BACKGROUND
):

    apply_global_theme(
        DASHBOARD_BACKGROUND
    )

else:

    apply_global_theme(
        None
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # BRAND
    # ========================================================

    st.title(
        "📊 RetailPulse"
    )

    st.subheader(
        "AI 2.0"
    )

    st.caption(
        "Retail Decision Intelligence Platform"
    )

    st.divider()


    # ========================================================
    # USER
    # ========================================================

    username_display = (
        st.session_state.username
        if st.session_state.username
        else "User"
    )


    with st.container(
        border=True
    ):

        st.caption(
            "SIGNED IN AS"
        )

        st.write(
            f"👤 **{username_display}**"
        )


    # ========================================================
    # DATASET STATUS
    # ========================================================

    if st.session_state.get(
        "dataset_configured",
        False
    ):

        st.success(
            "● Dataset Active"
        )

    else:

        st.warning(
            "● No Dataset Loaded"
        )


    # ========================================================
    # ACTIVE DATASET
    # ========================================================

    if (
        st.session_state.get(
            "dataset_configured",
            False
        )
        and
        st.session_state.get(
            "analysis_df"
        ) is not None
    ):

        analysis_df = (
            st.session_state.analysis_df
        )


        with st.expander(
            "Active Dataset",
            expanded=False
        ):

            file_name = (
                st.session_state.get(
                    "current_file_name"
                )
                or
                "Dataset"
            )


            st.write(
                f"**File:** {file_name}"
            )


            sheet_name = (
                st.session_state.get(
                    "current_sheet_name"
                )
            )


            if sheet_name:

                st.write(
                    f"**Sheet:** {sheet_name}"
                )


            st.write(
                f"**Rows:** {len(analysis_df):,}"
            )


            st.write(
                f"**Columns:** "
                f"{len(analysis_df.columns):,}"
            )


    st.divider()


# ============================================================
# NAVIGATION
# ============================================================

navigation_options = [

    "🏠 Dashboard",

    "📁 Data Upload",

    "📊 Analytics",

    "🤖 Forecasting",

    "💡 Business Insights",

    "⚙️ Dataset Info"
]


page = st.sidebar.radio(
    "NAVIGATION",
    navigation_options,
    key="main_navigation"
)


# ============================================================
# FORECAST SUMMARY
# ============================================================

with st.sidebar:

    if st.session_state.get(
        "lstm_trained",
        False
    ):

        st.divider()

        st.caption(
            "FORECAST STATUS"
        )


        best_model = (
            st.session_state.get(
                "best_model"
            )
        )


        best_mape = (
            st.session_state.get(
                "best_mape"
            )
        )


        forecast_change = (
            st.session_state.get(
                "percentage_change"
            )
        )


        forecast_target = (
            st.session_state.get(
                "forecast_target_used"
            )
        )


        if best_model:

            st.write(
                f"🏆 **{best_model}**"
            )


        if best_mape is not None:

            st.write(
                f"MAPE: **{best_mape:.2f}%**"
            )


        if forecast_change is not None:

            if forecast_change >= 0:

                st.write(
                    f"📈 Forecast: "
                    f"**+{forecast_change:.2f}%**"
                )

            else:

                st.write(
                    f"📉 Forecast: "
                    f"**{forecast_change:.2f}%**"
                )


        if forecast_target:

            st.caption(
                f"Target: {forecast_target}"
            )


    st.divider()


    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="logout_button"
    ):

        st.session_state.logged_in = False

        st.session_state.username = None

        st.rerun()


# ============================================================
# PAGE ROUTING
# ============================================================

if page == "🏠 Dashboard":

    show_dashboard()


elif page == "📁 Data Upload":

    show_data_upload()


elif page == "📊 Analytics":

    show_analytics()


elif page == "🤖 Forecasting":

    show_forecasting()


elif page == "💡 Business Insights":

    show_business_insights()


elif page == "⚙️ Dataset Info":

    show_dataset_info()


# ============================================================
# APPLICATION FOOTER
# ============================================================

st.divider()

st.caption(
    "RetailPulse AI 2.0 • Retail Analytics • "
    "Deep Learning Forecasting • "
    "Business Decision Intelligence"
)