# VPBank — eKYC & Credit Scoring ML Services

Banking ML portfolio: **credit scoring** (logistic regression on applicant features) and **eKYC** image verification (face detection, blur, document edge checks) exposed via a unified **FastAPI** service.

**Role:** Data Engineer · **Year:** 2019

## Tech Stack

| Module | Technology |
|--------|------------|
| Credit scoring | scikit-learn, StandardScaler + LogisticRegression |
| eKYC vision | OpenCV (Haar face cascade, Laplacian blur, Canny edges) |
| API | FastAPI, multipart upload |
| Model registry | Joblib artifacts under `models/` |

## Architecture

```mermaid
flowchart TB
    subgraph CHANNEL["📱 Digital Onboarding"]
        APP["Mobile / Web App"]
        ID["ID + Selfie Upload"]
        FORM["Loan Application Form"]
    end

    subgraph API["⚡ ML API Gateway"]
        GW["FastAPI<br/>/v1/ekyc/verify<br/>/v1/credit/score"]
    end

    subgraph ML["🤖 ML Services"]
        EKYC["eKYC Pipeline<br/>face • blur • doc edges"]
        CREDIT["Credit Model<br/>PD • score band • limit"]
    end

    subgraph CORE["🏦 Bank Systems"]
        LOS["Loan Origination"]
        CRM["Customer MDM"]
        AUDIT["Audit & Compliance log"]
    end

    APP --> ID --> GW
    APP --> FORM --> GW
    GW --> EKYC
    GW --> CREDIT
    EKYC --> LOS
    CREDIT --> LOS
    GW --> AUDIT
    LOS --> CRM

    style CHANNEL fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style API fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    style ML fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style CORE fill:#fce4ec,stroke:#c2185b,stroke-width:2px
```

## Score Bands

| Band | Default probability | Typical limit multiplier (× monthly income) |
|------|---------------------|-----------------------------------------------|
| A | &lt; 15% | 8× |
| B | 15–30% | 5× |
| C | 30–50% | 2× |
| D | ≥ 50% | 0 (manual review) |

## Quick Start

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python scripts/demo_run.py
uvicorn src.api.main:app --reload --port 8080
```

## API Examples

```bash
# Credit score
curl -X POST http://localhost:8080/v1/credit/score \
  -H "Content-Type: application/json" \
  -d "{\"age\":32,\"monthly_income_vnd\":25000000,\"employment_months\":48,\"existing_loans\":1,\"delinquency_12m\":0,\"credit_utilization_pct\":35}"

# eKYC (multipart)
curl -X POST http://localhost:8080/v1/ekyc/verify -F "file=@data/raw/sample_selfie.png"
```

## Repository Layout

```
vpbank-ekyc-credit-scoring/
├── src/credit/     # Scoring model train + inference
├── src/ekyc/       # Image verification heuristics
├── src/api/        # FastAPI gateway
├── models/         # Serialized pipelines
└── scripts/        # Local demo
```

## Production Notes

- Replace synthetic training data with governed feature store exports.
- Swap Haar cascade with ONNX face model + liveness detection in production.
- Log all scores with model version hash for regulatory audit.

---

*Portfolio reconstruction. No VPBank customer PII included.*
