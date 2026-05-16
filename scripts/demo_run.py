"""Train credit model and run sample eKYC on synthetic image."""

import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.credit.scoring_model import load_model, score_applicant
from src.ekyc.face_verify import analyze_id_selfie

MODEL = ROOT / "models" / "credit_score_v1.joblib"
SAMPLE_IMG = ROOT / "data" / "raw" / "sample_selfie.png"


def _create_sample_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = np.ones((480, 640, 3), dtype=np.uint8) * 220
    cv2.rectangle(img, (80, 120), (560, 400), (30, 30, 30), 3)
    cv2.circle(img, (320, 220), 60, (180, 160, 140), -1)
    cv2.imwrite(str(path), img)


def main() -> None:
    pipe = load_model(MODEL)
    credit = score_applicant(
        pipe,
        "demo-001",
        {
            "age": 32,
            "monthly_income_vnd": 25_000_000,
            "employment_months": 48,
            "existing_loans": 1,
            "delinquency_12m": 0,
            "credit_utilization_pct": 35.0,
        },
    )
    print("Credit:", credit)

    _create_sample_image(SAMPLE_IMG)
    ekyc = analyze_id_selfie(SAMPLE_IMG)
    print("eKYC:", ekyc)


if __name__ == "__main__":
    main()
