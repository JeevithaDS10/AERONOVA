# train_price_model.py

import os
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

from app.db import get_connection


def load_price_history_dataframe() -> pd.DataFrame:
    """Load data from price_history table into a pandas DataFrame."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            flight_id,
            base_price,
            final_price,
            days_to_departure,
            seats_left,
            is_weekend,
            delay_risk,
            route_popularity
        FROM price_history
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        raise RuntimeError("price_history table is empty. Run the generator first.")

    df = pd.DataFrame(rows)
    return df


def preprocess_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Convert raw DataFrame into feature matrix X and target y.
    - Encodes delay_risk from LOW/MEDIUM/HIGH to 0/1/2
    - Splits out final_price as target
    """
    risk_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    df["delay_risk_num"] = df["delay_risk"].map(risk_map)

    feature_cols = [
        "base_price",
        "days_to_departure",
        "seats_left",
        "is_weekend",
        "delay_risk_num",
        "route_popularity",
    ]

    X = df[feature_cols]
    y = df["final_price"]

    return X, y


def train_model(X: pd.DataFrame, y: pd.Series) -> RandomForestRegressor:
    """
    Train a RandomForestRegressor on the given features and target.
    Prints MAE on validation set.
    """
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, y_pred)
    print(f"Validation MAE: {mae:.2f}")

    return model


def save_model(model: RandomForestRegressor, path: str):
    """Save trained model to file using joblib."""
    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")


def main():
    print("Loading price_history data...")
    df = load_price_history_dataframe()
    print(f"Loaded {len(df)} rows")

    print("Preprocessing...")
    X, y = preprocess_dataframe(df)

    print("Training model...")
    model = train_model(X, y)

    save_model(model, "app/ml/model/price_model.pkl")


if __name__ == "__main__":
    main()
