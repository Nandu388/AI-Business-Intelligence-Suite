import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve, precision_recall_curve)
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import warnings; warnings.filterwarnings("ignore")

def train_churn_model(df, target_col, feature_cols, model_type="Random Forest", use_smote=True):
    X = df[feature_cols].copy()
    y = df[target_col].copy()

    # Ensure binary target
    if y.nunique() > 2:
        raise ValueError("Target column must be binary (0/1 or Yes/No).")
    if y.dtype == object:
        y = (y == y.unique()[1]).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    if use_smote and y_train.value_counts().min() > 5:
        sm = SMOTE(random_state=42)
        X_train_s, y_train = sm.fit_resample(X_train_s, y_train)

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=8,
                                                 class_weight="balanced", random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=150, max_depth=4,
                                                          learning_rate=0.05, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    }

    model = models[model_type]
    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]

    metrics = {
        "AUC-ROC": round(roc_auc_score(y_test, y_prob), 4),
        "Accuracy": round((y_pred == y_test).mean(), 4),
        "Report": classification_report(y_test, y_pred, output_dict=True),
        "Confusion Matrix": confusion_matrix(y_test, y_pred),
    }

    fpr, tpr, _ = roc_curve(y_test, y_prob)
    prec, rec, _ = precision_recall_curve(y_test, y_prob)

    importances = None
    if hasattr(model, "feature_importances_"):
        importances = dict(zip(feature_cols, model.feature_importances_))

    return model, scaler, metrics, fpr, tpr, prec, rec, importances

def predict_single(model, scaler, feature_cols, input_dict):
    row = pd.DataFrame([input_dict])[feature_cols]
    row_s = scaler.transform(row)
    prob = model.predict_proba(row_s)[0][1]
    label = "Likely to Churn" if prob > 0.5 else "Likely to Retain"
    return prob, label