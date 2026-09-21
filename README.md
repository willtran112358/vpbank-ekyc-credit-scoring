# VPBank — eKYC & Credit Scoring ML Services

Digital-bank **onboarding** for a VPBank-shaped retail bank: **eKYC** image checks + **application PD** via FastAPI, aligned to public product themes on [Cá nhân](https://www.vpbank.com.vn/ca-nhan) and [Hộ kinh doanh](https://www.vpbank.com.vn/ho-kinh-doanh).

Book-level IFRS 9 / ECL engine (after the loan exists): companion pattern in a credit-risk solution repo.

**Role:** Data Engineer · **Year:** 2019

---

## Digital bank onboarding

```mermaid
flowchart TB
    classDef ch fill:#E8F5E9,stroke:#1B5E20,stroke-width:2px,color:#1B5E20
    classDef api fill:#FFF8E1,stroke:#F9A825,stroke-width:2px,color:#E65100
    classDef ml fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    classDef core fill:#FCE4EC,stroke:#C2185B,stroke-width:2px,color:#880E4F

    subgraph CH["📱 Channels"]
        NEO["VPBank NEO"]:::ch
        AI["VP AI"]:::ch
        PT["Partners — Shopee · MWG"]:::ch
        BR["Branch / RM"]:::ch
    end

    subgraph API["⚡ FastAPI gateway"]
        GW["/v1/ekyc/verify<br/>/v1/credit/score"]:::api
    end

    subgraph ML["🤖 Decisioning"]
        EKYC["eKYC — face · blur · doc edges"]:::ml
        PD["Application PD · band A–D · limit"]:::ml
    end

    subgraph CORE["🏦 Bank"]
        LOS["Loan origination / card"]:::core
        CRM["Customer MDM"]:::core
        AUD["Audit log"]:::core
    end

    NEO --> GW
    AI --> GW
    PT --> GW
    BR --> GW
    GW --> EKYC --> LOS
    GW --> PD --> LOS
    GW --> AUD
    LOS --> CRM
```

## Product themes this API feeds

```mermaid
flowchart LR
    classDef per fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef card fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    classDef hkd fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px,color:#E65100

    E["eKYC + app score"] --> PL["Vay tín chấp<br/>lương · giáo viên · đảo nợ"]:::per
    E --> CC["Thẻ tín dụng<br/>MWG · Shopee · GameON · JCB<br/>Flex · Travel · Diamond World"]:::card
    E --> MTG["Vay thế chấp BĐS · VinFast"]:::per
    E --> HKD["CommCredit HKD<br/>tín chấp / thế chấp"]:::hkd
```

| Line | Public theme | Risk use of this API |
|------|----------------|----------------------|
| Cá nhân | [Vay tín chấp / thế chấp](https://www.vpbank.com.vn/ca-nhan/vay) | KYC gate + PD band before LOS |
| Cá nhân | [Thẻ tín dụng](https://www.vpbank.com.vn/ca-nhan/the-tin-dung) | Same PD bands; limit × income |
| HKD | [CommCredit](https://www.vpbank.com.vn/ho-kinh-doanh) | Onboarding KYC for hộ kinh doanh |
| Segments | Prime · Diamond · Private | Same API; policy overlay in LOS |

```mermaid
flowchart TB
    classDef s1 fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef s2 fill:#FFE082,stroke:#F9A825,stroke-width:2px,color:#E65100
    classDef s3 fill:#FFCCBC,stroke:#E64A19,stroke-width:2px,color:#BF360C
    classDef s4 fill:#EF9A9A,stroke:#C62828,stroke-width:2px,color:#B71C1C

    A["Band A · PD < 15% · limit 8× income"]:::s1 --> B["Band B · 15–30% · 5×"]:::s2
    B --> C["Band C · 30–50% · 2×"]:::s3
    C --> D["Band D · ≥ 50% · decline / manual"]:::s4
```

## Tech stack

| Module | Technology |
|--------|------------|
| Credit scoring | scikit-learn, StandardScaler + LogisticRegression |
| eKYC vision | OpenCV (Haar face cascade, Laplacian blur, Canny edges) |
| API | FastAPI, multipart upload |
| Model registry | Joblib artifacts under `models/` |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/demo_run.py
uvicorn src.api.main:app --reload --port 8080
```

## API examples

```bash
# Credit score
curl -X POST http://localhost:8080/v1/credit/score \
  -H "Content-Type: application/json" \
  -d "{\"age\":32,\"monthly_income_vnd\":25000000,\"employment_months\":48,\"existing_loans\":1,\"delinquency_12m\":0,\"credit_utilization_pct\":35}"

# eKYC (multipart)
curl -X POST http://localhost:8080/v1/ekyc/verify -F "file=@data/raw/sample_selfie.png"
```

## Layout

```
vpbank-ekyc-credit-scoring/
├── src/credit/     # Scoring model train + inference
├── src/ekyc/       # Image verification heuristics
├── src/api/        # FastAPI gateway
├── models/         # Serialized pipelines
└── scripts/        # Local demo
```

## Production notes

- Replace synthetic training data with governed feature store exports.
- Swap Haar cascade with ONNX face model + liveness detection in production.
- Log all scores with model version hash for regulatory audit.

---

*Portfolio reconstruction from public VPBank product pages. No customer PII.*

**WillTran** — Senior Data Engineer
