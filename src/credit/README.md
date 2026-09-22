<p align="center">
  <img src="../../docs/assets/logo-vpbank.svg" alt="VPBank" height="36">
</p>

# Credit scoring

Origination **PD** for VPBank [Cá nhân](https://www.vpbank.com.vn/ca-nhan) / [Hộ kinh doanh](https://www.vpbank.com.vn/ho-kinh-doanh) applications. Code: `scoring_model.py`. API: `POST /v1/credit/score`.

| ![Vay tín chấp](../../docs/assets/icons/icon-vay-tin-chap.svg) | ![Thẻ](../../docs/assets/icons/icon-the-tin-dung.svg) | ![Thế chấp](../../docs/assets/icons/icon-vay-the-chap.svg) |
|:---:|:---:|:---:|
| Unsecured PL | Cards | Mortgage / auto |

<p align="center">
  <img src="../../docs/assets/anh-khcn-1.png" alt="Cá nhân origination" height="160">
</p>

## Business requirement

| Need | Why |
|------|-----|
| Instant PD + band at apply | NEO / partner (Shopee, MWG) cannot wait T+1 |
| Limit suggestion | Band × monthly income (A 8×, B 5×, C 2×, D 0) |
| Same features, product overlay | PL, card, CommCredit share bureau-style inputs |
| Audit | Persist PD, band, model file (`credit_score_v1.joblib`) |

Inputs: `age`, `monthly_income_vnd`, `employment_months`, `existing_loans`, `delinquency_12m`, `credit_utilization_pct`.

## Solution architecture

```mermaid
flowchart LR
    classDef src fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef api fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    classDef mdl fill:#FFF9C4,stroke:#F9A825,stroke-width:2px,color:#F57F17
    classDef dec fill:#E1BEE7,stroke:#7B1FA2,stroke-width:2px,color:#4A148C

    A["Application JSON"]:::src --> B["FastAPI /v1/credit/score"]:::api
    B --> C["StandardScaler + LogReg"]:::mdl
    C --> D["PD"]:::mdl
    D --> E["Band A–D"]:::dec
    E --> F["Limit VND"]:::dec
    F --> G["LOS / card line"]:::src
```

Train (offline, synthetic book) → `joblib` → online `score_applicant`.

## Sample engineering code

```python
# scoring_model.py — inference
row = pd.DataFrame([{k: features[k] for k in FEATURE_COLUMNS}])
prob = float(pipe.predict_proba(row)[0][1])   # PD
band = "A" if prob < 0.15 else "B" if prob < 0.30 else "C" if prob < 0.50 else "D"
limit = int(income * {"A": 8, "B": 5, "C": 2, "D": 0}[band])
```

```bash
curl -X POST http://localhost:8080/v1/credit/score \
  -H "Content-Type: application/json" \
  -d '{"age":32,"monthly_income_vnd":25000000,"employment_months":48,"existing_loans":1,"delinquency_12m":0,"credit_utilization_pct":35}'
```

Holdout metric is stored on the joblib artifact. Swap synthetic labels for CIC / observed default before production.