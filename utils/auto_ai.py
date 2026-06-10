import pandas as pd
import numpy as np

# =========================================================
# AUTO DETECT BEST DATE COLUMN
# =========================================================
def detect_date_column(df):

    for col in df.columns:

        # skip IDs
        if any(

            x in col.lower()

            for x in [

                "id",

                "code",

                "number"
            ]
        ):

            continue

        try:

            converted = pd.to_datetime(

                df[col],

                errors="coerce"
            )

            valid_ratio = (

                converted.notna().sum()

                / len(df)
            )

            if valid_ratio > 0.6:

                return col

        except:
            pass

    return None


# =========================================================
# AUTO DETECT NUMERIC TARGET
# =========================================================
def detect_target_column(df):

    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    # remove IDs
    numeric_cols = [

        c for c in numeric_cols

        if "id" not in c.lower()
    ]

    if len(numeric_cols) > 0:

        # choose highest variance column
        variances = {

            col: df[col].var()

            for col in numeric_cols
        }

        return max(
            variances,
            key=variances.get
        )

    return None


# =========================================================
# GENERATE DATE IF NONE EXISTS
# =========================================================
def create_date_column(df):

    df = df.copy()

    df["Auto_Date"] = pd.date_range(

        start="2024-01-01",

        periods=len(df),

        freq="D"
    )

    return df, "Auto_Date"


# =========================================================
# REMOVE ID COLUMNS
# =========================================================
def remove_id_columns(df):

    remove_cols = []

    for col in df.columns:

        if any(

            x in col.lower()

            for x in [

                "id",

                "uuid",

                "code"
            ]
        ):

            remove_cols.append(col)

    return df.drop(
        columns=remove_cols,
        errors="ignore"
    )


# =========================================================
# AUTO PREPARE FORECAST DATA
# =========================================================
def auto_prepare_forecast(df):

    df = remove_id_columns(df)

    # detect date
    date_col = detect_date_column(df)

    # generate if missing
    if date_col is None:

        df, date_col = create_date_column(df)

    # detect target
    target_col = detect_target_column(df)

    # fallback
    if target_col is None:

        numeric_cols = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        if len(numeric_cols) == 0:

            # create synthetic numeric column
            df["Auto_Value"] = np.arange(
                len(df)
            )

            target_col = "Auto_Value"

        else:

            target_col = numeric_cols[0]

    return df, date_col, target_col