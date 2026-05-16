"""Unified eKYC + credit scoring API."""

from pathlib import Path
import tempfile
import uuid

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field

from src.credit.scoring_model import FEATURE_COLUMNS, load_model, score_applicant
from src.ekyc.face_verify import analyze_id_selfie

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "credit_score_v1.joblib"

app = FastAPI(title="VPBank eKYC & Credit Scoring", version="1.0.0")


class CreditRequest(BaseModel):
    applicant_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    age: int
    monthly_income_vnd: int
    employment_months: int
    existing_loans: int = 0
    delinquency_12m: int = 0
    credit_utilization_pct: float = 0.0


@app.get("/health")
def health():
    return {"status": "ok", "features": FEATURE_COLUMNS}


@app.post("/v1/credit/score")
def credit_score(req: CreditRequest):
    pipe = load_model(MODEL_PATH)
    result = score_applicant(pipe, req.applicant_id, req.model_dump())
    return {
        "applicant_id": result.applicant_id,
        "probability_default": result.probability_default,
        "score_band": result.score_band,
        "recommended_limit_vnd": result.recommended_limit_vnd,
    }


@app.post("/v1/ekyc/verify")
async def ekyc_verify(file: UploadFile = File(...)):
    suffix = Path(file.filename or "id.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    result = analyze_id_selfie(tmp_path)
    tmp_path.unlink(missing_ok=True)
    return {
        "passed": result.passed,
        "face_detected": result.face_detected,
        "blur_score": result.blur_score,
        "document_edge_score": result.document_edge_score,
        "reasons": result.reasons,
    }
