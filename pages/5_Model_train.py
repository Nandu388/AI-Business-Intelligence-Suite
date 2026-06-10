import streamlit as st
import pandas as pd
import numpy as np

from sklearn.model_selection import (
    train_test_split,
    cross_val_score
)

from sklearn.preprocessing import (
    LabelEncoder,
    StandardScaler
)

from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer

from sklearn.metrics import (

    accuracy_score,
    precision_score,
    recall_score,
    f1_score,

    mean_squared_error,
    r2_score
)

from sklearn.linear_model import (

    LogisticRegression,
    LinearRegression
)

from sklearn.ensemble import (

    RandomForestClassifier,
    RandomForestRegressor
)

import plotly.express as px

from utils.session_state import init_session

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(

    page_title="Model Training",

    layout="wide"
)

# =====================================================
# INIT SESSION
# =====================================================
init_session()

st.title("⚙️ Model Training & Comparison")

# =====================================================
# LOAD DATA
# =====================================================
df = (

    st.session_state.df_processed

    if st.session_state.get("df_processed") is not None

    else st.session_state.get("df")
)

# =====================================================
# CHECK DATA
# =====================================================
if df is None:

    st.warning(
        "Please upload dataset first."
    )

    st.stop()

# =====================================================
# REMOVE DUPLICATE COLUMNS
# =====================================================
df = df.loc[:, ~df.columns.duplicated()]

# =====================================================
# HANDLE DATE COLUMNS
# =====================================================
for col in df.columns:

    try:

        if (

            "date" in col.lower()

            or

            "time" in col.lower()
        ):

            df[col] = pd.to_datetime(

                df[col],

                errors="coerce"
            )

            df[col] = (

                df[col].astype("int64")

                // 10**9
            )

    except:
        pass

# =====================================================
# ENCODE OBJECT COLUMNS
# =====================================================
for col in df.columns:

    try:

        if df[col].dtype == "object":

            le = LabelEncoder()

            df[col] = le.fit_transform(

                df[col].astype(str)
            )

    except:
        pass

# =====================================================
# NUMERIC COLUMNS
# =====================================================
numeric_cols = df.select_dtypes(

    include=np.number

).columns.tolist()

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:

    st.header("⚙️ Training Settings")

    # -------------------------------------------------
    # TASK TYPE
    # -------------------------------------------------
    task_type = st.radio(

        "Task Type",

        [
            "Classification",
            "Regression"
        ]
    )

    # -------------------------------------------------
    # TARGET
    # -------------------------------------------------
    target_col = st.selectbox(

        "Target Column",

        numeric_cols
    )

    # -------------------------------------------------
    # FEATURES
    # -------------------------------------------------
    feature_cols = st.multiselect(

        "Feature Columns",

        [
            c for c in numeric_cols
            if c != target_col
        ],

        default=[
            c for c in numeric_cols
            if c != target_col
        ][:5]
    )

    # -------------------------------------------------
    # TEST SIZE
    # -------------------------------------------------
    test_size = st.slider(

        "Test Split %",

        10,
        40,
        20
    )

    # -------------------------------------------------
    # CROSS VALIDATION
    # -------------------------------------------------
    cv_folds = st.slider(

        "Cross Validation Folds",

        2,
        10,
        5
    )

    # -------------------------------------------------
    # TRAIN BUTTON
    # -------------------------------------------------
    train_btn = st.button(

        "🚀 Train Models",

        type="primary"
    )

# =====================================================
# TRAINING
# =====================================================
if train_btn:

    # =================================================
    # FEATURE CHECK
    # =================================================
    if len(feature_cols) == 0:

        st.warning(
            "Please select feature columns."
        )

        st.stop()

    try:

        # =============================================
        # MODEL DATA
        # =============================================
        model_df = df[
            feature_cols + [target_col]
        ].copy()

        # =============================================
        # DROP MISSING
        # =============================================
        model_df = model_df.dropna()

        # =============================================
        # SMALL DATA CHECK
        # =============================================
        if len(model_df) < 20:

            st.warning(
                "Dataset too small for training."
            )

            st.stop()

        # =============================================
        # FEATURES / TARGET
        # =============================================
        X = model_df[feature_cols]

        y = model_df[target_col]

        # =============================================
        # CLASSIFICATION CHECK
        # =============================================
        if task_type == "Classification":

            # -----------------------------------------
            # CONTINUOUS DATA CHECK
            # -----------------------------------------
            if y.nunique() > 10:

                st.warning(
                    f"""
                    ❌ '{target_col}' looks continuous.

                    Classification cannot be performed.

                    Please choose Regression.
                    """
                )

                st.stop()

            # -----------------------------------------
            # MIN CLASS COUNT
            # -----------------------------------------
            min_class = y.value_counts().min()

            if min_class < 2:

                st.warning(
                    """
                    ❌ Some classes contain
                    very few samples.
                    """
                )

                st.stop()

            # -----------------------------------------
            # FIX CV FOLDS
            # -----------------------------------------
            if cv_folds > min_class:

                st.warning(
                    f"""
                    Cross Validation folds reduced
                    from {cv_folds} to {min_class}
                    because dataset is small.
                    """
                )

                cv_folds = min_class

        # =============================================
        # SPLIT DATA
        # =============================================
        try:

            stratify_option = (

                y

                if task_type == "Classification"

                else None
            )

            X_train, X_test, y_train, y_test = train_test_split(

                X,
                y,

                test_size=test_size / 100,

                random_state=42,

                stratify=stratify_option
            )

        except:

            st.warning(
                """
                ❌ Dataset cannot be split properly.

                Please choose another target column.
                """
            )

            st.stop()

        # =============================================
        # MODELS
        # =============================================
        if task_type == "Classification":

            models = {

                "Logistic Regression":
                    LogisticRegression(
                        max_iter=1000
                    ),

                "Random Forest":
                    RandomForestClassifier(
                        n_estimators=100,
                        random_state=42
                    )
            }

        else:

            models = {

                "Linear Regression":
                    LinearRegression(),

                "Random Forest":
                    RandomForestRegressor(
                        n_estimators=100,
                        random_state=42
                    )
            }

        # =============================================
        # RESULTS
        # =============================================
        results = []

        st.subheader("📊 Model Results")

        # =============================================
        # TRAIN EACH MODEL
        # =============================================
        for model_name, model in models.items():

            try:

                # -------------------------------------
                # PIPELINE
                # -------------------------------------
                pipeline = Pipeline([

                    (
                        "imputer",
                        SimpleImputer(
                            strategy="mean"
                        )
                    ),

                    (
                        "scaler",
                        StandardScaler()
                    ),

                    (
                        "model",
                        model
                    )
                ])

                # -------------------------------------
                # TRAIN
                # -------------------------------------
                pipeline.fit(
                    X_train,
                    y_train
                )

                # -------------------------------------
                # PREDICT
                # -------------------------------------
                predictions = pipeline.predict(
                    X_test
                )

                # -------------------------------------
                # CROSS VALIDATION
                # -------------------------------------
                try:

                    if task_type == "Classification":

                        cv_score = cross_val_score(

                            pipeline,

                            X,
                            y,

                            cv=cv_folds,

                            scoring="accuracy"
                        ).mean()

                    else:

                        cv_score = cross_val_score(

                            pipeline,

                            X,
                            y,

                            cv=cv_folds,

                            scoring="r2"
                        ).mean()

                except:

                    cv_score = 0

                # -------------------------------------
                # CLASSIFICATION METRICS
                # -------------------------------------
                if task_type == "Classification":

                    accuracy = accuracy_score(
                        y_test,
                        predictions
                    )

                    precision = precision_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0
                    )

                    recall = recall_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0
                    )

                    f1 = f1_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0
                    )

                    results.append({

                        "Model":
                            model_name,

                        "Accuracy":
                            round(accuracy, 4),

                        "Precision":
                            round(precision, 4),

                        "Recall":
                            round(recall, 4),

                        "F1 Score":
                            round(f1, 4),

                        "CV Score":
                            round(cv_score, 4)
                    })

                # -------------------------------------
                # REGRESSION METRICS
                # -------------------------------------
                else:

                    rmse = np.sqrt(

                        mean_squared_error(
                            y_test,
                            predictions
                        )
                    )

                    r2 = r2_score(
                        y_test,
                        predictions
                    )

                    results.append({

                        "Model":
                            model_name,

                        "RMSE":
                            round(rmse, 4),

                        "R²":
                            round(r2, 4),

                        "CV Score":
                            round(cv_score, 4)
                    })

            except:

                st.info(
                    f"""
                    {model_name}
                    could not train on this dataset.
                    """
                )

        # =============================================
        # NO RESULTS
        # =============================================
        if len(results) == 0:

            st.warning(
                """
                ❌ No models could train
                on this dataset.
                """
            )

            st.stop()

        # =============================================
        # RESULTS DATAFRAME
        # =============================================
        results_df = pd.DataFrame(results)

        st.dataframe(

            results_df,

            use_container_width=True
        )

        # =============================================
        # CHART
        # =============================================
        try:

            metric_col = (

                "Accuracy"

                if task_type == "Classification"

                else "R²"
            )

            fig = px.bar(

                results_df,

                x="Model",

                y=metric_col,

                color="Model",

                text=metric_col,

                title="Model Comparison"
            )

            fig.update_layout(

                template="plotly_dark",

                height=500
            )

            st.plotly_chart(

                fig,

                use_container_width=True
            )

        except:
            pass

        # =============================================
        # DOWNLOAD
        # =============================================
        st.download_button(

            "⬇️ Download Results CSV",

            results_df.to_csv(index=False),

            "model_results.csv",

            "text/csv"
        )

        st.success(
            "✅ Model training completed successfully!"
        )

    except:

        st.warning(
            """
            ❌ This dataset is not suitable
            for the selected task.
            """
        )

# =====================================================
# DEFAULT MESSAGE
# =====================================================
else:

    st.info(
        """
        Select task type,
        target column,
        feature columns,
        and click Train Models.
        """
    )