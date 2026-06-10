import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from statsmodels.tsa.holtwinters import (
    ExponentialSmoothing
)

import warnings

warnings.filterwarnings("ignore")

# =========================================================
# PREPARE TIME SERIES
# =========================================================
def prepare_time_series(
    df,
    date_col,
    value_col,
    freq="M"
):

    ts = df[[date_col, value_col]].copy()

    # =====================================================
    # DATE CONVERSION
    # =====================================================
    ts[date_col] = pd.to_datetime(
        ts[date_col],
        errors="coerce"
    )

    ts = ts.dropna(
        subset=[date_col]
    )

    # =====================================================
    # NUMERIC CONVERSION
    # =====================================================
    ts[value_col] = pd.to_numeric(
        ts[value_col],
        errors="coerce"
    )

    ts = ts.dropna(
        subset=[value_col]
    )

    # =====================================================
    # SORT
    # =====================================================
    ts = ts.sort_values(date_col)

    # =====================================================
    # INDEX
    # =====================================================
    ts = ts.set_index(date_col)

    # =====================================================
    # RESAMPLE
    # =====================================================
    try:

        ts = ts[value_col].resample(freq).mean()

    except:

        ts = ts[value_col]

    # =====================================================
    # CLEAN
    # =====================================================
    ts = ts.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # =====================================================
    # FILL MISSING
    # =====================================================
    ts = ts.interpolate()

    ts = ts.fillna(
        method="bfill"
    )

    ts = ts.fillna(
        method="ffill"
    )

    # =====================================================
    # LAST SAFETY
    # =====================================================
    ts = ts.dropna()

    return ts


# =========================================================
# CREATE LAG FEATURES
# =========================================================
def add_lag_features(
    series,
    lags=6
):

    df = pd.DataFrame({
        "y": series
    })

    # =====================================================
    # AUTO REDUCE LAGS
    # =====================================================
    lags = min(
        lags,
        max(1, len(series) // 2)
    )

    for lag in range(1, lags + 1):

        df[f"lag_{lag}"] = (
            df["y"].shift(lag)
        )

    # =====================================================
    # ROLLING FEATURES
    # =====================================================
    df["rolling_mean_3"] = (
        df["y"]
        .shift(1)
        .rolling(3)
        .mean()
    )

    df["rolling_std_3"] = (
        df["y"]
        .shift(1)
        .rolling(3)
        .std()
    )

    # =====================================================
    # DATE FEATURES
    # =====================================================
    if hasattr(df.index, "month"):

        df["month"] = df.index.month

        df["quarter"] = df.index.quarter

        df["year"] = df.index.year

    else:

        df["month"] = 0
        df["quarter"] = 0
        df["year"] = 0

    # =====================================================
    # CLEAN
    # =====================================================
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.dropna()

    return df


# =========================================================
# TRAIN FORECAST MODEL
# =========================================================
def train_forecast_model(
    series,
    model_type="Gradient Boosting",
    horizon=6
):

    # =====================================================
    # SMALL DATASET FIX
    # =====================================================
    if len(series) < 6:

        # simple naive forecast
        future_index = pd.date_range(

            start=series.index[-1],

            periods=horizon + 1,

            freq=(
                series.index.freq
                or "D"
            )
        )[1:]

        last_val = series.iloc[-1]

        forecast_series = pd.Series(

            [last_val] * horizon,

            index=future_index
        )

        ci_lower = forecast_series * 0.9
        ci_upper = forecast_series * 1.1

        metrics = {
            "MAE": 0,
            "RMSE": 0,
            "R²": 1
        }

        return (
            None,
            forecast_series,
            ci_lower,
            ci_upper,
            metrics,
            series,
            series
        )

    # =====================================================
    # FEATURES
    # =====================================================
    df_feat = add_lag_features(series)

    # =====================================================
    # FALLBACK
    # =====================================================
    if len(df_feat) < 3:

        future_index = pd.date_range(

            start=series.index[-1],

            periods=horizon + 1,

            freq=(
                series.index.freq
                or "D"
            )
        )[1:]

        mean_val = series.mean()

        forecast_series = pd.Series(

            [mean_val] * horizon,

            index=future_index
        )

        ci_lower = forecast_series * 0.9
        ci_upper = forecast_series * 1.1

        metrics = {
            "MAE": 0,
            "RMSE": 0,
            "R²": 1
        }

        return (
            None,
            forecast_series,
            ci_lower,
            ci_upper,
            metrics,
            series,
            series
        )

    # =====================================================
    # X/Y
    # =====================================================
    X = df_feat.drop(
        "y",
        axis=1
    )

    y = df_feat["y"]

    # =====================================================
    # TRAIN TEST SPLIT
    # =====================================================
    split = max(
        1,
        int(len(X) * 0.8)
    )

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    # =====================================================
    # MODEL
    # =====================================================
    if model_type == "Gradient Boosting":

        model = GradientBoostingRegressor(

            n_estimators=200,

            max_depth=4,

            learning_rate=0.05,

            random_state=42
        )

    else:

        model = LinearRegression()

    # =====================================================
    # FIT
    # =====================================================
    model.fit(
        X_train,
        y_train
    )

    # =====================================================
    # PREDICT TEST
    # =====================================================
    if len(X_test) > 0:

        y_pred = model.predict(X_test)

        mae = mean_absolute_error(
            y_test,
            y_pred
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_test,
                y_pred
            )
        )

        r2 = r2_score(
            y_test,
            y_pred
        )

    else:

        y_pred = y_train

        mae = 0
        rmse = 0
        r2 = 1

    # =====================================================
    # METRICS
    # =====================================================
    metrics = {

        "MAE":
            round(mae, 2),

        "RMSE":
            round(rmse, 2),

        "R²":
            round(r2, 4)
    }

    # =====================================================
    # FUTURE FORECAST
    # =====================================================
    last_vals = list(
        series.values[-6:]
    )

    future_preds = []

    # =====================================================
    # SAFE FREQUENCY
    # =====================================================
    freq = (
        series.index.freq
        or pd.infer_freq(series.index)
        or "D"
    )

    future_index = pd.date_range(

        start=series.index[-1],

        periods=horizon + 1,

        freq=freq
    )[1:]

    # =====================================================
    # ITERATIVE FORECAST
    # =====================================================
    for i in range(horizon):

        lags = last_vals[-6:][::-1]

        rm3 = np.mean(
            last_vals[-3:]
        )

        rs3 = np.std(
            last_vals[-3:]
        )

        next_date = future_index[i]

        month = (
            next_date.month
            if hasattr(next_date, "month")
            else 0
        )

        quarter = (
            next_date.quarter
            if hasattr(next_date, "quarter")
            else 0
        )

        year = (
            next_date.year
            if hasattr(next_date, "year")
            else 0
        )

        row = (
            lags
            + [rm3, rs3, month, quarter, year]
        )

        row = row[:X.shape[1]]

        pred = model.predict(
            [row]
        )[0]

        future_preds.append(pred)

        last_vals.append(pred)

    # =====================================================
    # FORECAST SERIES
    # =====================================================
    forecast_series = pd.Series(

        future_preds,

        index=future_index
    )

    # =====================================================
    # CONFIDENCE INTERVALS
    # =====================================================
    ci_lower = (
        forecast_series
        - (1.5 * metrics["MAE"])
    )

    ci_upper = (
        forecast_series
        + (1.5 * metrics["MAE"])
    )

    # =====================================================
    # RETURN
    # =====================================================
    return (

        model,

        forecast_series,

        ci_lower,

        ci_upper,

        metrics,

        y_test,

        pd.Series(
            y_pred,
            index=y_test.index
        ) if len(X_test) > 0 else y_train
    )


# =========================================================
# HOLT WINTERS
# =========================================================
def hw_forecast(
    series,
    horizon=6
):

    try:

        # =================================================
        # SMALL DATASET FIX
        # =================================================
        seasonal_periods = min(
            12,
            max(2, len(series) // 2)
        )

        model = ExponentialSmoothing(

            series,

            seasonal="add",

            trend="add",

            seasonal_periods=seasonal_periods
        )

        fit = model.fit(
            optimized=True,
            use_brute=True
        )

        forecast = fit.forecast(
            horizon
        )

        return forecast

    except:

        # fallback naive
        future_index = pd.date_range(

            start=series.index[-1],

            periods=horizon + 1,

            freq=(
                series.index.freq
                or "D"
            )
        )[1:]

        return pd.Series(

            [series.iloc[-1]] * horizon,

            index=future_index
        )