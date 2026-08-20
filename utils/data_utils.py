import os
import pandas as pd


# ============================================================
# HELPERS
# ============================================================

def _validate_uploaded_file(uploaded_file):
    """
    Validate that an uploaded file object is available
    and contains a usable file name.
    """

    if uploaded_file is None:
        raise ValueError(
            "No file was uploaded."
        )

    file_name = getattr(
        uploaded_file,
        "name",
        None
    )

    if not file_name:
        raise ValueError(
            "Uploaded file does not have a valid file name."
        )

    return str(
        file_name
    ).strip()


def _reset_file_pointer(uploaded_file):
    """
    Reset uploaded file pointer when supported.
    """

    try:
        uploaded_file.seek(0)
    except Exception:
        pass


def _clean_column_names(df):
    """
    Clean dataframe column names and make duplicates unique.
    """

    if df is None:
        return df

    cleaned_columns = []

    seen = {}


    for column in df.columns:

        cleaned = str(
            column
        ).strip()


        if cleaned == "":
            cleaned = "Unnamed Column"


        if cleaned not in seen:

            seen[cleaned] = 0

            cleaned_columns.append(
                cleaned
            )

        else:

            seen[cleaned] += 1

            unique_name = (
                f"{cleaned}_{seen[cleaned]}"
            )

            while unique_name in seen:

                seen[cleaned] += 1

                unique_name = (
                    f"{cleaned}_{seen[cleaned]}"
                )

            seen[
                unique_name
            ] = 0

            cleaned_columns.append(
                unique_name
            )


    df.columns = (
        cleaned_columns
    )

    return df


# ============================================================
# GET EXCEL SHEET NAMES
# ============================================================

def get_excel_sheets(
    uploaded_file
):
    """
    Return all worksheet names from an uploaded
    XLSX Excel workbook.
    """

    if uploaded_file is None:
        return []


    file_name = _validate_uploaded_file(
        uploaded_file
    )


    extension = os.path.splitext(
        file_name
    )[1].lower()


    if extension != ".xlsx":
        return []


    _reset_file_pointer(
        uploaded_file
    )


    try:

        excel_file = pd.ExcelFile(
            uploaded_file,
            engine="openpyxl"
        )


        sheet_names = list(
            excel_file.sheet_names
        )


    finally:

        _reset_file_pointer(
            uploaded_file
        )


    return sheet_names


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset(
    uploaded_file,
    sheet_name=None
):
    """
    Load CSV or XLSX retail data.

    Parameters
    ----------
    uploaded_file :
        Streamlit UploadedFile or compatible file-like object.

    sheet_name : str or None
        Excel worksheet name when loading XLSX.

    Supported formats
    -----------------
    CSV
    XLSX

    Returns
    -------
    pandas.DataFrame
    """

    file_name = _validate_uploaded_file(
        uploaded_file
    )


    extension = os.path.splitext(
        file_name
    )[1].lower()


    _reset_file_pointer(
        uploaded_file
    )


    try:

        # ====================================================
        # CSV
        # ====================================================

        if extension == ".csv":

            try:

                df = pd.read_csv(
                    uploaded_file,
                    low_memory=False
                )

            except UnicodeDecodeError:

                _reset_file_pointer(
                    uploaded_file
                )

                # Common fallback for older CSV exports.
                df = pd.read_csv(
                    uploaded_file,
                    encoding="latin-1",
                    low_memory=False
                )


        # ====================================================
        # EXCEL
        # ====================================================

        elif extension == ".xlsx":

            if sheet_name is None:

                df = pd.read_excel(
                    uploaded_file,
                    engine="openpyxl"
                )

            else:

                df = pd.read_excel(
                    uploaded_file,
                    sheet_name=sheet_name,
                    engine="openpyxl"
                )


        # ====================================================
        # UNSUPPORTED FILE
        # ====================================================

        else:

            raise ValueError(
                "Unsupported file format. "
                "Please upload a CSV or XLSX file."
            )


    finally:

        _reset_file_pointer(
            uploaded_file
        )


    # ========================================================
    # RESULT VALIDATION
    # ========================================================

    if df is None:

        raise ValueError(
            "The uploaded file could not be converted "
            "into a dataset."
        )


    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "The loaded file did not produce "
            "a pandas DataFrame."
        )


    # ========================================================
    # CLEAN COLUMN NAMES
    # ========================================================

    df = _clean_column_names(
        df
    )


    return df


# ============================================================
# DATASET SUMMARY
# ============================================================

def get_dataset_summary(
    df
):
    """
    Return basic dataset statistics.
    """

    if df is None:

        return {
            "rows": 0,
            "columns": 0,
            "missing_values": 0,
            "duplicate_rows": 0
        }


    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "Dataset must be a pandas DataFrame."
        )


    rows = int(
        df.shape[0]
    )


    columns = int(
        df.shape[1]
    )


    missing_values = int(
        df
        .isna()
        .sum()
        .sum()
    )


    duplicate_rows = int(
        df
        .duplicated()
        .sum()
    )


    return {

        "rows":
            rows,

        "columns":
            columns,

        "missing_values":
            missing_values,

        "duplicate_rows":
            duplicate_rows
    }


# ============================================================
# COLUMN INFORMATION
# ============================================================

def get_column_information(
    df
):
    """
    Return structural and quality information
    for every dataframe column.
    """

    if df is None:

        return pd.DataFrame(
            columns=[
                "Column",
                "Data Type",
                "Missing Values",
                "Missing (%)",
                "Unique Values"
            ]
        )


    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "Dataset must be a pandas DataFrame."
        )


    total_rows = len(
        df
    )


    column_rows = []


    for column in df.columns:

        series = df[
            column
        ]


        missing_values = int(
            series
            .isna()
            .sum()
        )


        if total_rows > 0:

            missing_percentage = (
                missing_values
                /
                total_rows
            ) * 100

        else:

            missing_percentage = 0.0


        unique_values = int(
            series
            .nunique(
                dropna=True
            )
        )


        column_rows.append(
            {
                "Column":
                    str(column),

                "Data Type":
                    str(
                        series.dtype
                    ),

                "Missing Values":
                    missing_values,

                "Missing (%)":
                    round(
                        missing_percentage,
                        2
                    ),

                "Unique Values":
                    unique_values
            }
        )


    return pd.DataFrame(
        column_rows
    )