import pandas as pd
import numpy as np

from sklearn.preprocessing import (
    LabelEncoder,
    StandardScaler
)

from sklearn.impute import (
    SimpleImputer
)

import warnings

warnings.filterwarnings("ignore")

# =========================================================
# LOAD DATA
# =========================================================
def load_data(file):

    # =====================================================
    # CSV
    # =====================================================
    if file.name.endswith(".csv"):

        try:

            df = pd.read_csv(
                file,
                low_memory=False
            )

        except:

            df = pd.read_csv(
                file,
                encoding="latin1",
                low_memory=False
            )

    # =====================================================
    # EXCEL
    # =====================================================
    elif file.name.endswith(

        (".xlsx", ".xls")

    ):

        df = pd.read_excel(file)

    else:

        raise ValueError(
            "Unsupported file type."
        )

    # =====================================================
    # REMOVE EMPTY ROWS/COLS
    # =====================================================
    df = df.dropna(
        how="all"
    )

    df = df.dropna(
        axis=1,
        how="all"
    )

    # =====================================================
    # RESET INDEX
    # =====================================================
    df = df.reset_index(
        drop=True
    )

    return df


# =========================================================
# COLUMN TYPES
# =========================================================
def get_column_types(df):

    df = df.copy()

    # =====================================================
    # NUMERIC
    # =====================================================
    numeric_cols = df.select_dtypes(

        include=np.number

    ).columns.tolist()

    # =====================================================
    # CATEGORICAL
    # =====================================================
    categorical_cols = df.select_dtypes(

        include=[
            "object",
            "category",
            "bool"
        ]

    ).columns.tolist()

    # =====================================================
    # DATETIME
    # =====================================================
    datetime_cols = []

    # already datetime
    datetime_cols.extend(

        df.select_dtypes(
            include=["datetime64"]
        ).columns.tolist()
    )

    # =====================================================
    # DETECT DATETIME STRINGS
    # =====================================================
    for col in categorical_cols.copy():

        try:

            converted = pd.to_datetime(

                df[col],

                errors="coerce"
            )

            valid_ratio = (

                converted.notna().sum()

                / len(df)
            )

            # at least 60% valid
            if valid_ratio > 0.6:

                datetime_cols.append(col)

                categorical_cols.remove(col)

        except:
            pass

    return (

        numeric_cols,

        categorical_cols,

        datetime_cols
    )


# =========================================================
# BASIC INFO
# =========================================================
def basic_info(df):

    total_cells = (

        df.shape[0]

        * df.shape[1]
    )

    if total_cells == 0:

        missing_pct = 0

    else:

        missing_pct = round(

            (

                df.isnull()
                .sum()
                .sum()

                / total_cells

            ) * 100,

            2
        )

    info = {

        "rows":
            len(df),

        "columns":
            len(df.columns),

        "missing_pct":
            missing_pct,

        "duplicates":
            int(
                df.duplicated().sum()
            ),

        "memory_mb":
            round(

                df.memory_usage(
                    deep=True
                ).sum()

                / 1024**2,

                3
            )
    }

    return info


# =========================================================
# PREPROCESS
# =========================================================
def preprocess_df(

    df,

    drop_thresh=0.6,

    scale=True
):

    df = df.copy()

    # =====================================================
    # REMOVE DUPLICATE COLUMNS
    # =====================================================
    df = df.loc[
        :,
        ~df.columns.duplicated()
    ]

    # =====================================================
    # REMOVE EMPTY ROWS
    # =====================================================
    df = df.dropna(
        how="all"
    )

    # =====================================================
    # DROP HIGH-MISSING COLUMNS
    # =====================================================
    thresh = int(
        drop_thresh * len(df)
    )

    df.dropna(

        axis=1,

        thresh=thresh,

        inplace=True
    )

    # =====================================================
    # DROP DUPLICATES
    # =====================================================
    df.drop_duplicates(
        inplace=True
    )

    # =====================================================
    # REPLACE INF
    # =====================================================
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # =====================================================
    # COLUMN TYPES
    # =====================================================
    (
        numeric_cols,

        categorical_cols,

        datetime_cols

    ) = get_column_types(df)

    # =====================================================
    # DATETIME CONVERSION
    # =====================================================
    for col in datetime_cols:

        try:

            df[col] = pd.to_datetime(

                df[col],

                errors="coerce"
            )

            # extract features
            df[f"{col}_year"] = (
                df[col].dt.year
            )

            df[f"{col}_month"] = (
                df[col].dt.month
            )

            df[f"{col}_day"] = (
                df[col].dt.day
            )

            df[f"{col}_weekday"] = (
                df[col].dt.weekday
            )

        except:
            pass

    # =====================================================
    # REFRESH TYPES
    # =====================================================
    (
        numeric_cols,

        categorical_cols,

        datetime_cols

    ) = get_column_types(df)

    # =====================================================
    # NUMERIC IMPUTE
    # =====================================================
    if len(numeric_cols) > 0:

        try:

            imp_num = SimpleImputer(
                strategy="median"
            )

            df[numeric_cols] = (
                imp_num.fit_transform(
                    df[numeric_cols]
                )
            )

        except:
            pass

    # =====================================================
    # CATEGORICAL IMPUTE
    # =====================================================
    if len(categorical_cols) > 0:

        try:

            imp_cat = SimpleImputer(
                strategy="most_frequent"
            )

            df[categorical_cols] = (
                imp_cat.fit_transform(
                    df[categorical_cols]
                )
            )

        except:
            pass

    # =====================================================
    # ENCODING
    # =====================================================
    encoders = {}

    for col in categorical_cols:

        try:

            le = LabelEncoder()

            df[col] = le.fit_transform(

                df[col]
                .astype(str)
            )

            encoders[col] = le

        except:
            pass

    # =====================================================
    # SCALING
    # =====================================================
    if scale and len(numeric_cols) > 0:

        try:

            scaler = StandardScaler()

            df[numeric_cols] = (
                scaler.fit_transform(
                    df[numeric_cols]
                )
            )

        except:
            pass

    # =====================================================
    # FINAL CLEAN
    # =====================================================
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.fillna(0)

    df = df.reset_index(
        drop=True
    )

    return df


# =========================================================
# OUTLIER SUMMARY
# =========================================================
def get_outlier_summary(df):

    numeric_cols = df.select_dtypes(

        include=np.number

    ).columns

    results = []

    # =====================================================
    # LOOP
    # =====================================================
    for col in numeric_cols:

        try:

            series = pd.to_numeric(

                df[col],

                errors="coerce"
            )

            series = series.dropna()

            if len(series) == 0:
                continue

            Q1 = series.quantile(0.25)

            Q3 = series.quantile(0.75)

            IQR = Q3 - Q1

            lower = (
                Q1 - 1.5 * IQR
            )

            upper = (
                Q3 + 1.5 * IQR
            )

            outliers = (

                (
                    series < lower
                )

                |

                (
                    series > upper
                )

            ).sum()

            results.append({

                "Column":
                    col,

                "Outliers":
                    int(outliers),

                "Pct":
                    round(
                        outliers / len(series) * 100,
                        2
                    )
            })

        except:
            pass

    # =====================================================
    # RETURN
    # =====================================================
    if len(results) == 0:

        return pd.DataFrame()

    return pd.DataFrame(results)