"""Credit scoring — logistic regression on anonymized applicant features."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class CreditScoreResult:
    applicant_id: str
    probability_default: float
    score_band: str  # A, B, C, D
    recommended_limit_vnd: int


FEATURE_COLUMNS = [
    "age",
    "monthly_income_vnd",
    "employment_months",
    "existing_loans",
    "delinquency_12m",
    "credit_utilization_pct",
]


def synthetic_training_data(n: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "age": rng.integers(22, 55, n),
            "monthly_income_vnd": rng.integers(8_000_000, 80_000_000, n),
            "employment_months": rng.integers(3, 120, n),
            "existing_loans": rng.integers(0, 4, n),
            "delinquency_12m": rng.integers(0, 3, n),
            "credit_utilization_pct": rng.uniform(0, 95, n).round(1),
        }
    )
    # Higher risk when delinquency + utilization high
    risk = (
        0.4 * (df["delinquency_12m"] > 0)
        + 0.3 * (df["credit_utilization_pct"] > 70)
        + 0.2 * (df["monthly_income_vnd"] < 15_000_000)
        + 0.1 * (df["existing_loans"] > 2)
    )
    df["default_flag"] = (risk + rng.random(n) * 0.2 > 0.55).astype(int)
    return df


def train_model(model_path: Path) -> Pipeline:
    df = synthetic_training_data()
    X = df[FEATURE_COLUMNS]
    y = df["default_flag"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipe = Pipeline([("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))])
    pipe.fit(X_train, y_train)
    acc = pipe.score(X_test, y_test)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "metrics": {"holdout_accuracy": acc}}, model_path)
    return pipe


def load_model(model_path: Path) -> Pipeline:
    if not model_path.exists():
        train_model(model_path)
    artifact = joblib.load(model_path)
    return artifact["pipeline"]


def score_applicant(pipe: Pipeline, applicant_id: str, features: dict) -> CreditScoreResult:
    row = pd.DataFrame([{k: features[k] for k in FEATURE_COLUMNS}])
    prob = float(pipe.predict_proba(row)[0][1])
    band = _band(prob)
    limit = _limit_from_band(band, features["monthly_income_vnd"])
    return CreditScoreResult(
        applicant_id=applicant_id,
        probability_default=round(prob, 4),
        score_band=band,
        recommended_limit_vnd=limit,
    )


def _band(prob: float) -> str:
    if prob < 0.15:
        return "A"
    if prob < 0.30:
        return "B"
    if prob < 0.50:
        return "C"
    return "D"


def _limit_from_band(band: str, income: float) -> int:
    multipliers = {"A": 8, "B": 5, "C": 2, "D": 0}
    return int(income * multipliers.get(band, 0))
