# ============================================================
# HELPERS
# ============================================================

def normalize_column_name(value):
    """
    Normalize a column name or keyword so matching is
    case-insensitive and robust to underscores, hyphens
    and extra spaces.
    """

    if value is None:
        return ""

    normalized = (
        str(value)
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .strip()
    )

    normalized = " ".join(
        normalized.split()
    )

    return normalized


# ============================================================
# COLUMN DETECTION
# ============================================================

def detect_column(
    columns,
    keywords
):
    """
    Automatically detect a dataset column using a list
    of possible retail-related keywords.

    Matching order:
    1. Exact normalized match
    2. Keyword contained in column name
    3. Column name contained in keyword

    Returns
    -------
    str
        Matching original dataset column name,
        otherwise "None".
    """

    if not columns:
        return "None"

    if not keywords:
        return "None"


    # ========================================================
    # NORMALIZE AVAILABLE COLUMNS
    # ========================================================

    normalized_columns = []

    for column in columns:

        normalized_columns.append(
            (
                column,
                normalize_column_name(
                    column
                )
            )
        )


    # ========================================================
    # NORMALIZE KEYWORDS
    # ========================================================

    normalized_keywords = []

    for keyword in keywords:

        normalized = normalize_column_name(
            keyword
        )

        if normalized:
            normalized_keywords.append(
                normalized
            )


    if not normalized_keywords:
        return "None"


    # ========================================================
    # 1. EXACT MATCH
    # ========================================================

    for keyword in normalized_keywords:

        for (
            original_column,
            normalized_column
        ) in normalized_columns:

            if normalized_column == keyword:

                return original_column


    # ========================================================
    # 2. KEYWORD INSIDE COLUMN NAME
    # ========================================================

    # Prefer longer keywords first.
    # This helps choose "product name" before "product".
    sorted_keywords = sorted(
        normalized_keywords,
        key=len,
        reverse=True
    )


    for keyword in sorted_keywords:

        for (
            original_column,
            normalized_column
        ) in normalized_columns:

            if keyword in normalized_column:

                return original_column


    # ========================================================
    # 3. COLUMN NAME INSIDE KEYWORD
    # ========================================================

    for (
        original_column,
        normalized_column
    ) in normalized_columns:

        if not normalized_column:
            continue

        for keyword in sorted_keywords:

            if normalized_column in keyword:

                return original_column


    # ========================================================
    # NO MATCH
    # ========================================================

    return "None"


# ============================================================
# SELECTBOX INDEX
# ============================================================

def get_selected_index(
    options,
    value
):
    """
    Return the safe Streamlit selectbox index for a
    detected or previously configured column.

    Falls back to the first option, which is normally "None".
    """

    if not options:
        return 0


    if value is None:
        return 0


    if value in options:

        return options.index(
            value
        )


    # ========================================================
    # NORMALIZED FALLBACK MATCH
    # ========================================================

    normalized_value = normalize_column_name(
        value
    )


    if normalized_value:

        for index, option in enumerate(
            options
        ):

            if (
                normalize_column_name(
                    option
                )
                ==
                normalized_value
            ):

                return index


    return 0