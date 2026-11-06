"""
====================================================================
Machine Learning Training Pipeline: Student Performance Prediction
Algorithm: Random Forest Regression (Scikit-Learn)
====================================================================
Steps:
1. Load student academic dataset from CSV
2. Data preprocessing & missing value handling
3. Feature selection (Attendance, Prev Marks, Internal, Study Hours, Assignments, Absences)
4. Train/Test split (80% train, 20% test)
5. Model training using RandomForestRegressor
6. Model evaluation (MAE, MSE, RMSE, R² Score)
7. Save model to Joblib format (.pkl)
"""

import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'student_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'student_performance_model.pkl')
METRICS_PATH = os.path.join(MODEL_DIR, 'model_metrics.json')

def train_and_save_model(dataset_file=DATASET_PATH):
    print("---------------------------------------------------------------")
    print(" [1/6] Loading Student Academic Dataset...")
    print(f" Source: {dataset_file}")
    
    if not os.path.exists(dataset_file):
        raise FileNotFoundError(f"Dataset file not found at {dataset_file}")
    
    df = pd.read_csv(dataset_file)
    print(f" Loaded {len(df)} rows with columns: {list(df.columns)}")

    # [2/6] Missing value handling
    print(" [2/6] Preprocessing and handling missing values...")
    df = df.dropna()

    # [3/6] Feature selection
    feature_cols = [
        'attendance',
        'previous_marks',
        'internal_marks',
        'study_hours',
        'assignment_score',
        'absences'
    ]
    target_col = 'final_marks'

    X = df[feature_cols]
    y = df[target_col]

    # [4/6] Train-Test Split (80% Training, 20% Testing)
    print(" [4/6] Splitting data into 80% Train, 20% Test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # [5/6] Model Training using Random Forest Regressor
    print(" [5/6] Training Random Forest Regressor (n_estimators=100, max_depth=8)...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        min_samples_split=3,
        random_state=42
    )
    model.fit(X_train, y_train)

    # [6/6] Evaluation on Test Set
    print(" [6/6] Evaluating Model Performance on Test Data...")
    y_pred = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    # Feature Importance analysis
    importances = model.feature_importances_
    feature_importance_list = [
        {"feature": col, "importance": round(float(imp) * 100, 2)}
        for col, imp in sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
    ]

    metrics = {
        "mae": round(mae, 2),
        "mse": round(mse, 2),
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importances": feature_importance_list,
        "algorithm": "RandomForestRegressor(n_estimators=100, max_depth=8)"
    }

    print("---------------------------------------------------------------")
    print(f" Model Evaluation Results:")
    print(f" - MAE  (Mean Absolute Error):     {metrics['mae']}")
    print(f" - MSE  (Mean Squared Error):      {metrics['mse']}")
    print(f" - RMSE (Root Mean Squared Error): {metrics['rmse']}")
    print(f" - R²   (Coefficient of Determ.):  {metrics['r2_score']}")
    print("---------------------------------------------------------------")

    # Ensure models directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Save model using Joblib
    joblib.dump(model, MODEL_PATH)
    print(f" Model serialized and saved to: {MODEL_PATH}")

    # Save metrics JSON
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f" Metrics stored at: {METRICS_PATH}")

    return metrics

if __name__ == '__main__':
    train_and_save_model()
