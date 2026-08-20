import streamlit as st
import pandas as pd

from utils.data_utils import (
    load_dataset,
    get_excel_sheets,
    get_dataset_summary,
    get_column_information
)

from utils.column_detection import (
    detect_column,
    get_selected_index
)

from utils.preprocessing import (
    preprocess_retail_data
)


# ============================================================
# DATASET SESSION KEYS
# ============================================================

DATASET_STATE_KEYS = [
    "dataset_configured",

    "retail_df",
    "analysis_df",

    "current_file_name",
    "current_sheet_name",

    "date_column",
    "sales_column",
    "quantity_column",
    "product_column",
    "category_column",
    "region_column",
    "customer_column",

    "lstm_trained",

    "mae",
    "rmse",
    "mape",
    "r2",

    "comparison_df",
    "future_df",
    "loss_df",
    "combined_df",
    "model_comparison",

    "best_model",
    "best_mape",

    "percentage_change",
    "epochs_used",

    "forecast_frequency",
    "forecast_target_used"
]


# ============================================================
# FORECAST / MODEL STATE KEYS
# ============================================================

MODEL_STATE_KEYS = [
    "lstm_trained",

    "mae",
    "rmse",
    "mape",
    "r2",

    "comparison_df",
    "future_df",
    "loss_df",
    "combined_df",
    "model_comparison",

    "best_model",
    "best_mape",

    "percentage_change",
    "epochs_used",

    "forecast_frequency",
    "forecast_target_used"
]


# ============================================================
# CONFIGURATION STATE KEYS
# ============================================================

CONFIGURATION_STATE_KEYS = [
    "dataset_configured",

    "analysis_df",

    "date_column",
    "sales_column",
    "quantity_column",
    "product_column",
    "category_column",
    "region_column",
    "customer_column"
] + MODEL_STATE_KEYS


# ============================================================
# CLEAR ONLY DATASET STATE
# ============================================================

def clear_dataset():

    for key in DATASET_STATE_KEYS:

        if key in st.session_state:
            del st.session_state[key]


# ============================================================
# CLEAR CONFIGURATION / FORECAST STATE
# ============================================================

def clear_configuration_state():

    for key in CONFIGURATION_STATE_KEYS:

        if key in st.session_state:
            del st.session_state[key]


# ============================================================
# CLEAR ONLY FORECAST STATE
# ============================================================

def clear_forecast_state():

    for key in MODEL_STATE_KEYS:

        if key in st.session_state:
            del st.session_state[key]

    # Restore the main trained flag explicitly.
    st.session_state.lstm_trained = False


# ============================================================
# SHOW CURRENT ACTIVE DATASET
# ============================================================

def show_active_dataset():

    if not st.session_state.get(
        "dataset_configured",
        False
    ):
        return False

    analysis_df = st.session_state.get(
        "analysis_df"
    )

    if analysis_df is None:
        return False

    if analysis_df.empty:
        return False

    st.success(
        "✅ A dataset is already loaded and active."
    )

    file_name = (
        st.session_state.get(
            "current_file_name"
        )
        or
        "Retail Dataset"
    )

    sheet_name = st.session_state.get(
        "current_sheet_name"
    )

    a1, a2, a3 = st.columns(3)

    with a1:

        st.metric(
            "Active File",
            file_name
        )

    with a2:

        st.metric(
            "Rows",
            f"{len(analysis_df):,}"
        )

    with a3:

        st.metric(
            "Columns",
            f"{len(analysis_df.columns):,}"
        )

    if sheet_name:

        st.info(
            f"📑 Active worksheet: **{sheet_name}**"
        )

    st.caption(
        "This dataset remains active while you move between "
        "Dashboard, Analytics, Forecasting, Business Insights "
        "and Dataset Info."
    )

    return True


# ============================================================
# AUTOMATIC COLUMN DETECTION
# ============================================================

def detect_retail_columns(columns):

    detected_date = detect_column(
        columns,
        [
            "order date",
            "transaction date",
            "invoice date",
            "sales date",
            "purchase date",
            "date"
        ]
    )

    detected_sales = detect_column(
        columns,
        [
            "sales",
            "total sales",
            "net sales",
            "revenue",
            "amount",
            "turnover"
        ]
    )

    detected_quantity = detect_column(
        columns,
        [
            "quantity",
            "units sold",
            "units",
            "demand",
            "qty"
        ]
    )

    detected_product = detect_column(
        columns,
        [
            "product name",
            "product",
            "item name",
            "item",
            "sku"
        ]
    )

    detected_category = detect_column(
        columns,
        [
            "category",
            "product category",
            "department"
        ]
    )

    detected_region = detect_column(
        columns,
        [
            "region",
            "market",
            "territory",
            "location"
        ]
    )

    detected_customer = detect_column(
        columns,
        [
            "customer name",
            "customer",
            "client",
            "buyer"
        ]
    )

    return {
        "date": detected_date,
        "sales": detected_sales,
        "quantity": detected_quantity,
        "product": detected_product,
        "category": detected_category,
        "region": detected_region,
        "customer": detected_customer
    }


# ============================================================
# BUILD DETECTION TABLE
# ============================================================

def build_detection_table(detected):

    return pd.DataFrame(
        {
            "Retail Field": [
                "Date",
                "Sales / Revenue",
                "Quantity / Demand",
                "Product",
                "Category",
                "Region",
                "Customer"
            ],

            "Detected Column": [
                detected.get("date"),
                detected.get("sales"),
                detected.get("quantity"),
                detected.get("product"),
                detected.get("category"),
                detected.get("region"),
                detected.get("customer")
            ]
        }
    )


# ============================================================
# GET DEFAULT COLUMN
# ============================================================

def get_default_column(
    session_key,
    detected_value,
    options
):

    existing_value = st.session_state.get(
        session_key
    )

    if existing_value in options:
        return existing_value

    if detected_value in options:
        return detected_value

    return "None"


# ============================================================
# MAIN DATA UPLOAD PAGE
# ============================================================

def show_data_upload():

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.title(
        "📁 Data Upload & Configuration"
    )

    st.caption(
        "Upload and configure the retail dataset used throughout "
        "RetailPulse AI."
    )


    # ========================================================
    # ACTIVE DATASET
    # ========================================================

    active_dataset = show_active_dataset()

    if active_dataset:

        col1, col2 = st.columns(
            [3, 1]
        )

        with col1:

            st.info(
                "You do not need to upload the dataset again "
                "when switching between dashboard pages."
            )

        with col2:

            if st.button(
                "🗑️ Remove Dataset",
                use_container_width=True,
                key="remove_active_dataset"
            ):

                clear_dataset()

                st.rerun()

        st.divider()

        st.subheader(
            "📤 Replace Current Dataset"
        )

    else:

        st.subheader(
            "📤 Upload Dataset"
        )


    # ========================================================
    # FILE UPLOAD
    # ========================================================

    uploaded_file = st.file_uploader(
        "Choose CSV or Excel file",
        type=[
            "csv",
            "xlsx"
        ],
        key="retail_upload_widget"
    )


    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------
    # The uploader may visually reset when this page is not
    # rendered. That does not remove the dataframe already
    # stored in Streamlit session state.
    # --------------------------------------------------------

    if uploaded_file is None:

        if active_dataset:
            return

        st.info(
            "Upload a CSV or XLSX retail dataset to continue."
        )

        return


    # ========================================================
    # DETECT FILE CHANGE
    # ========================================================

    uploaded_name = uploaded_file.name

    current_name = st.session_state.get(
        "current_file_name"
    )

    is_new_file = (
        current_name != uploaded_name
    )


    # ========================================================
    # EXCEL WORKSHEET
    # ========================================================

    selected_sheet = None

    if uploaded_name.lower().endswith(
        ".xlsx"
    ):

        try:

            sheet_names = get_excel_sheets(
                uploaded_file
            )

        except Exception as e:

            st.error(
                "Unable to inspect the Excel workbook."
            )

            st.exception(e)

            return

        if not sheet_names:

            st.error(
                "No worksheets were detected."
            )

            return

        st.subheader(
            "📑 Select Excel Worksheet"
        )

        # -----------------------------------------------
        # Preserve previous worksheet if it still exists.
        # -----------------------------------------------

        previous_sheet = st.session_state.get(
            "current_sheet_name"
        )

        if previous_sheet in sheet_names:

            default_sheet_index = (
                sheet_names.index(
                    previous_sheet
                )
            )

        else:

            default_sheet_index = 0

        selected_sheet = st.selectbox(
            "Worksheet to analyze",
            options=sheet_names,
            index=default_sheet_index,
            key="retail_excel_sheet"
        )

        st.caption(
            f"Workbook contains {len(sheet_names)} worksheet(s): "
            + ", ".join(sheet_names)
        )


    # ========================================================
    # LOAD DATA
    # ========================================================

    try:

        # UploadedFile can be reused, but reset the pointer
        # before passing it to a utility when possible.
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

        df = load_dataset(
            uploaded_file,
            sheet_name=selected_sheet
        )

    except Exception as e:

        st.error(
            "Unable to load the selected dataset."
        )

        st.exception(e)

        return


    # ========================================================
    # VALIDATE DATAFRAME
    # ========================================================

    if df is None:

        st.error(
            "The selected dataset could not be loaded."
        )

        return

    if df.empty:

        st.error(
            "The selected dataset is empty."
        )

        return

    if len(df.columns) == 0:

        st.error(
            "No columns were detected in the dataset."
        )

        return


    # ========================================================
    # NORMALIZE COLUMN NAMES
    # ========================================================

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]


    # ========================================================
    # CHECK WHETHER SOURCE CHANGED
    # ========================================================

    previous_sheet = st.session_state.get(
        "current_sheet_name"
    )

    sheet_changed = (
        previous_sheet != selected_sheet
    )

    if is_new_file or sheet_changed:

        # Clear the previous dataset configuration and all
        # forecasting/model outputs while keeping authentication.
        clear_configuration_state()


    # ========================================================
    # STORE RAW DATA IMMEDIATELY
    # ========================================================

    st.session_state.retail_df = (
        df.copy()
    )

    st.session_state.current_file_name = (
        uploaded_name
    )

    st.session_state.current_sheet_name = (
        selected_sheet
    )


    # ========================================================
    # LOAD SUCCESS MESSAGE
    # ========================================================

    if selected_sheet:

        st.success(
            f"✅ {uploaded_name} → {selected_sheet} loaded."
        )

    else:

        st.success(
            f"✅ {uploaded_name} loaded."
        )


    # ========================================================
    # DATASET OVERVIEW
    # ========================================================

    try:

        summary = get_dataset_summary(
            df
        )

    except Exception as e:

        st.error(
            "Unable to calculate the dataset summary."
        )

        st.exception(e)

        return


    st.subheader(
        "📌 Dataset Overview"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Rows",
            f"{summary.get('rows', len(df)):,}"
        )

    with c2:

        st.metric(
            "Columns",
            f"{summary.get('columns', len(df.columns)):,}"
        )

    with c3:

        st.metric(
            "Missing Values",
            f"{summary.get('missing_values', 0):,}"
        )

    with c4:

        st.metric(
            "Duplicate Rows",
            f"{summary.get('duplicate_rows', 0):,}"
        )


    # ========================================================
    # PREVIEW
    # ========================================================

    with st.expander(
        "👀 Dataset Preview",
        expanded=False
    ):

        st.dataframe(
            df.head(25),
            use_container_width=True
        )


    # ========================================================
    # COLUMN INFORMATION
    # ========================================================

    with st.expander(
        "🔎 Column Information",
        expanded=False
    ):

        try:

            column_information = (
                get_column_information(
                    df
                )
            )

            st.dataframe(
                column_information,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:

            st.warning(
                "Column information could not be generated."
            )

            st.exception(e)


    # ========================================================
    # COLUMN DETECTION
    # ========================================================

    st.divider()

    st.subheader(
        "🧠 Automatic Retail Field Detection"
    )

    columns = list(
        df.columns
    )

    detected = detect_retail_columns(
        columns
    )

    detection_df = build_detection_table(
        detected
    )

    st.dataframe(
        detection_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "RetailPulse automatically suggests likely retail "
        "columns. Review the selections below before confirming."
    )


    # ========================================================
    # COLUMN CONFIGURATION
    # ========================================================

    st.divider()

    st.subheader(
        "⚙️ Configure Retail Columns"
    )

    options = [
        "None"
    ] + columns


    # ========================================================
    # DEFAULT VALUES
    # ========================================================

    date_default = get_default_column(
        "date_column",
        detected.get("date"),
        options
    )

    sales_default = get_default_column(
        "sales_column",
        detected.get("sales"),
        options
    )

    quantity_default = get_default_column(
        "quantity_column",
        detected.get("quantity"),
        options
    )

    product_default = get_default_column(
        "product_column",
        detected.get("product"),
        options
    )

    category_default = get_default_column(
        "category_column",
        detected.get("category"),
        options
    )

    region_default = get_default_column(
        "region_column",
        detected.get("region"),
        options
    )

    customer_default = get_default_column(
        "customer_column",
        detected.get("customer"),
        options
    )


    # ========================================================
    # COLUMN SELECTORS
    # ========================================================

    left, right = st.columns(2)


    # --------------------------------------------------------
    # LEFT SIDE
    # --------------------------------------------------------

    with left:

        date_column = st.selectbox(
            "📅 Date Column",
            options,
            index=get_selected_index(
                options,
                date_default
            ),
            key="config_date_column"
        )

        sales_column = st.selectbox(
            "💰 Sales / Revenue",
            options,
            index=get_selected_index(
                options,
                sales_default
            ),
            key="config_sales_column"
        )

        quantity_column = st.selectbox(
            "📦 Quantity / Demand",
            options,
            index=get_selected_index(
                options,
                quantity_default
            ),
            key="config_quantity_column"
        )

        product_column = st.selectbox(
            "🛍️ Product",
            options,
            index=get_selected_index(
                options,
                product_default
            ),
            key="config_product_column"
        )


    # --------------------------------------------------------
    # RIGHT SIDE
    # --------------------------------------------------------

    with right:

        category_column = st.selectbox(
            "🏷️ Category",
            options,
            index=get_selected_index(
                options,
                category_default
            ),
            key="config_category_column"
        )

        region_column = st.selectbox(
            "🌍 Region",
            options,
            index=get_selected_index(
                options,
                region_default
            ),
            key="config_region_column"
        )

        customer_column = st.selectbox(
            "👤 Customer",
            options,
            index=get_selected_index(
                options,
                customer_default
            ),
            key="config_customer_column"
        )


    # ========================================================
    # CONFIGURATION INFORMATION
    # ========================================================

    st.info(
        "📅 Date is required. For forecasting, select at least "
        "one target: **Sales / Revenue** or "
        "**Quantity / Demand**."
    )


    # ========================================================
    # CONFIRM CONFIGURATION
    # ========================================================

    st.divider()

    if st.button(
        "✅ Confirm Dataset Configuration",
        type="primary",
        use_container_width=True,
        key="confirm_dataset_configuration"
    ):

        # ====================================================
        # VALIDATE DATE COLUMN
        # ====================================================

        if date_column == "None":

            st.error(
                "A Date column is required."
            )

            return


        # ====================================================
        # VALIDATE FORECAST TARGET
        # ====================================================

        if (
            sales_column == "None"
            and
            quantity_column == "None"
        ):

            st.error(
                "Select at least one forecasting target: "
                "Sales / Revenue or Quantity / Demand."
            )

            return


        # ====================================================
        # VERIFY DATE COLUMN EXISTS
        # ====================================================

        if date_column not in df.columns:

            st.error(
                "The selected Date column does not exist "
                "in the dataset."
            )

            return


        # ====================================================
        # VERIFY SALES COLUMN
        # ====================================================

        if (
            sales_column != "None"
            and
            sales_column not in df.columns
        ):

            st.error(
                "The selected Sales column does not exist "
                "in the dataset."
            )

            return


        # ====================================================
        # VERIFY QUANTITY COLUMN
        # ====================================================

        if (
            quantity_column != "None"
            and
            quantity_column not in df.columns
        ):

            st.error(
                "The selected Quantity column does not exist "
                "in the dataset."
            )

            return


        # ====================================================
        # CONVERT NONE SELECTIONS
        # ====================================================

        preprocessing_sales_column = (
            None
            if sales_column == "None"
            else sales_column
        )

        preprocessing_quantity_column = (
            None
            if quantity_column == "None"
            else quantity_column
        )


        # ====================================================
        # PREPROCESS DATA
        # ====================================================

        try:

            analysis_df, invalid_dates = (
                preprocess_retail_data(
                    df=df,
                    date_column=date_column,
                    sales_column=preprocessing_sales_column,
                    quantity_column=preprocessing_quantity_column
                )
            )

        except Exception as e:

            st.error(
                "Dataset preprocessing failed."
            )

            st.exception(e)

            return


        # ====================================================
        # VALIDATE PROCESSED DATA
        # ====================================================

        if analysis_df is None:

            st.error(
                "Preprocessing did not return a valid dataset."
            )

            return

        if analysis_df.empty:

            st.error(
                "No usable records remain after preprocessing."
            )

            return


        # ====================================================
        # RESET PREVIOUS FORECAST
        # ====================================================

        clear_forecast_state()


        # ====================================================
        # SAVE RAW AND CLEANED DATA
        # ====================================================

        st.session_state.retail_df = (
            df.copy()
        )

        st.session_state.analysis_df = (
            analysis_df.copy()
        )


        # ====================================================
        # SAVE COLUMN CONFIGURATION
        # ====================================================

        st.session_state.date_column = (
            date_column
        )

        st.session_state.sales_column = (
            None
            if sales_column == "None"
            else sales_column
        )

        st.session_state.quantity_column = (
            None
            if quantity_column == "None"
            else quantity_column
        )

        st.session_state.product_column = (
            None
            if product_column == "None"
            else product_column
        )

        st.session_state.category_column = (
            None
            if category_column == "None"
            else category_column
        )

        st.session_state.region_column = (
            None
            if region_column == "None"
            else region_column
        )

        st.session_state.customer_column = (
            None
            if customer_column == "None"
            else customer_column
        )


        # ====================================================
        # MARK DATASET AS CONFIGURED
        # ====================================================

        st.session_state.dataset_configured = True


        # ====================================================
        # SUCCESS
        # ====================================================

        st.success(
            "✅ Dataset successfully configured and stored."
        )


        # ====================================================
        # INVALID DATE WARNING
        # ====================================================

        if invalid_dates > 0:

            st.warning(
                f"{invalid_dates:,} invalid date row(s) "
                "were removed during preprocessing."
            )


        # ====================================================
        # PROCESSED DATASET SUMMARY
        # ====================================================

        p1, p2 = st.columns(2)

        with p1:

            st.metric(
                "Usable Rows",
                f"{len(analysis_df):,}"
            )

        with p2:

            st.metric(
                "Usable Columns",
                f"{len(analysis_df.columns):,}"
            )


        # ====================================================
        # NEXT STEP
        # ====================================================

        st.info(
            "The dataset will remain active while you navigate "
            "between all RetailPulse dashboard pages.\n\n"
            "You can now open **🏠 Dashboard**."
        )