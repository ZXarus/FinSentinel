"""
Bank-Grade Financial Risk Flagging System - FastAPI Backend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
import io
import json
import warnings
warnings.filterwarnings("ignore")

# ML & Explainability
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import shap

app = FastAPI(
    title="Bank-Grade Financial Risk Flagging System",
    description="Detects financial manipulation using ML + SHAP explainability",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────

class ManualInputData(BaseModel):
    company_name: Optional[str] = "Unknown"
    revenue: float
    net_income: float
    total_assets: float
    total_liabilities: float
    cash_flow_operations: float
    total_debt: float
    accounts_receivable: float
    equity: float
    operating_income: Optional[float] = None
    model_type: str = "random_forest"  # "random_forest" or "linear_regression"

class BatchPredictRequest(BaseModel):
    model_type: str = "random_forest"

class PredictionResponse(BaseModel):
    company_name: str
    manipulation_flag: int
    manipulation_probability: float
    risk_level: str
    risk_score: float
    key_metrics: Dict[str, float]
    shap_values: Optional[Dict[str, float]] = None
    alerts: List[str]

# ─────────────────────────────────────────────
# Core Feature Engineering
# ─────────────────────────────────────────────

def compute_features(row: dict) -> dict:
    """Derive financial ratios used as ML features."""
    rev = row.get("revenue", 1) or 1
    assets = row.get("total_assets", 1) or 1
    equity = row.get("equity", 1) or 1
    net_income = row.get("net_income", 0)
    liabilities = row.get("total_liabilities", 0)
    cash_flow = row.get("cash_flow_operations", 0)
    debt = row.get("total_debt", 0)
    receivables = row.get("accounts_receivable", 0)
    op_income = row.get("operating_income") or net_income

    # Ratios
    debt_to_equity = debt / max(abs(equity), 1)
    net_margin = net_income / rev
    roa = net_income / assets
    current_ratio = (assets - liabilities) / max(assets * 0.3, 1)
    receivables_to_revenue = receivables / rev
    cash_flow_to_income = cash_flow / max(abs(net_income), 1)
    accruals = (net_income - cash_flow) / assets
    asset_growth = (assets - liabilities) / assets
    liabilities_to_assets = liabilities / assets
    op_margin = op_income / rev

    return {
        "debt_to_equity": debt_to_equity,
        "net_margin": net_margin,
        "roa": roa,
        "receivables_to_revenue": receivables_to_revenue,
        "cash_flow_to_income": cash_flow_to_income,
        "accruals": accruals,
        "asset_growth": asset_growth,
        "liabilities_to_assets": liabilities_to_assets,
        "op_margin": op_margin,
        # Raw inputs kept for display
        "revenue": row.get("revenue", 0),
        "net_income": net_income,
        "total_assets": assets,
        "total_liabilities": liabilities,
        "cash_flow_operations": cash_flow,
        "total_debt": debt,
        "accounts_receivable": receivables,
        "equity": equity,
    }

# ─────────────────────────────────────────────
# Risk Scoring Logic (rule-based + ML hybrid)
# ─────────────────────────────────────────────

FEATURE_NAMES = [
    "debt_to_equity", "net_margin", "roa",
    "receivables_to_revenue", "cash_flow_to_income",
    "accruals", "asset_growth", "liabilities_to_assets", "op_margin"
]

def rule_based_risk_score(features: dict) -> float:
    """Heuristic risk score based on financial red flags (0–1)."""
    score = 0.0
    flags = 0

    # Red flag: high accruals (earnings manipulation signal)
    if abs(features["accruals"]) > 0.10:
        score += 0.20; flags += 1

    # Red flag: cash flow << net income (Beneish-style)
    if features["cash_flow_to_income"] < 0.5:
        score += 0.20; flags += 1

    # Red flag: high receivables relative to revenue
    if features["receivables_to_revenue"] > 0.30:
        score += 0.15; flags += 1

    # Red flag: high debt-to-equity
    if features["debt_to_equity"] > 2.0:
        score += 0.15; flags += 1

    # Red flag: negative ROA
    if features["roa"] < 0:
        score += 0.15; flags += 1

    # Red flag: liabilities > 80% of assets
    if features["liabilities_to_assets"] > 0.80:
        score += 0.10; flags += 1

    # Red flag: negative operating margin
    if features["op_margin"] < 0:
        score += 0.05; flags += 1

    return min(score, 1.0)


def train_model(model_type: str = "random_forest"):
    """Train model on synthetic but realistic financial dataset."""
    np.random.seed(42)
    n = 500

    # Generate synthetic clean company data
    clean = {
        "debt_to_equity": np.random.uniform(0.2, 1.5, n // 2),
        "net_margin": np.random.uniform(0.05, 0.25, n // 2),
        "roa": np.random.uniform(0.03, 0.15, n // 2),
        "receivables_to_revenue": np.random.uniform(0.05, 0.20, n // 2),
        "cash_flow_to_income": np.random.uniform(0.8, 1.5, n // 2),
        "accruals": np.random.uniform(-0.05, 0.05, n // 2),
        "asset_growth": np.random.uniform(0.1, 0.4, n // 2),
        "liabilities_to_assets": np.random.uniform(0.2, 0.55, n // 2),
        "op_margin": np.random.uniform(0.05, 0.20, n // 2),
    }
    # Generate synthetic manipulated company data
    manip = {
        "debt_to_equity": np.random.uniform(1.8, 6.0, n // 2),
        "net_margin": np.random.uniform(-0.05, 0.10, n // 2),
        "roa": np.random.uniform(-0.10, 0.03, n // 2),
        "receivables_to_revenue": np.random.uniform(0.25, 0.70, n // 2),
        "cash_flow_to_income": np.random.uniform(-0.5, 0.5, n // 2),
        "accruals": np.random.uniform(0.10, 0.40, n // 2),
        "asset_growth": np.random.uniform(0.5, 1.2, n // 2),
        "liabilities_to_assets": np.random.uniform(0.70, 0.99, n // 2),
        "op_margin": np.random.uniform(-0.15, 0.05, n // 2),
    }

    df_clean = pd.DataFrame(clean)
    df_clean["label"] = 0
    df_manip = pd.DataFrame(manip)
    df_manip["label"] = 1

    df = pd.concat([df_clean, df_manip], ignore_index=True).sample(frac=1, random_state=42)
    X = df[FEATURE_NAMES].values
    y = df["label"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if model_type == "random_forest":
        model = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
    else:
        model = LogisticRegression(max_iter=500, random_state=42, C=1.0)

    model.fit(X_scaled, y)
    return model, scaler


def get_shap_values(model, scaler, feature_vec: np.ndarray, model_type: str) -> dict:
    """Compute SHAP values for a single prediction."""
    try:
        X_scaled = scaler.transform(feature_vec.reshape(1, -1))
        if model_type == "random_forest":
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(X_scaled)
            # For binary classification, shap_values returns list[2]
            if isinstance(shap_vals, list):
                vals = shap_vals[1][0]
            else:
                vals = shap_vals[0]
        else:
            explainer = shap.LinearExplainer(model, X_scaled)
            shap_vals = explainer.shap_values(X_scaled)
            if isinstance(shap_vals, list):
                vals = shap_vals[1][0]
            else:
                vals = shap_vals[0]
        return {FEATURE_NAMES[i]: float(vals[i]) for i in range(len(FEATURE_NAMES))}
    except Exception as e:
        return {f: 0.0 for f in FEATURE_NAMES}


def generate_alerts(features: dict, prob: float) -> list:
    alerts = []
    if abs(features["accruals"]) > 0.10:
        alerts.append("⚠️ High accruals detected — possible earnings inflation")
    if features["cash_flow_to_income"] < 0.5:
        alerts.append("⚠️ Cash flow significantly below net income — Beneish M-Score signal")
    if features["receivables_to_revenue"] > 0.30:
        alerts.append("⚠️ Excessive receivables relative to revenue — possible fictitious sales")
    if features["debt_to_equity"] > 2.0:
        alerts.append("⚠️ High debt-to-equity ratio — elevated financial leverage risk")
    if features["roa"] < 0:
        alerts.append("⚠️ Negative return on assets — company is losing value")
    if features["liabilities_to_assets"] > 0.80:
        alerts.append("⚠️ Liabilities exceed 80% of assets — near-insolvency risk")
    if features["op_margin"] < 0:
        alerts.append("⚠️ Negative operating margin — core business not profitable")
    if prob > 0.75:
        alerts.append("🚨 HIGH probability of financial manipulation — immediate review recommended")
    elif prob > 0.50:
        alerts.append("🔶 MODERATE manipulation risk — further due diligence advised")
    if not alerts:
        alerts.append("✅ No major red flags detected")
    return alerts


def predict_single(data: dict, model_type: str = "random_forest") -> PredictionResponse:
    features = compute_features(data)
    model, scaler = train_model(model_type)

    feature_vec = np.array([features[f] for f in FEATURE_NAMES])
    X_scaled = scaler.transform(feature_vec.reshape(1, -1))
    ml_prob = float(model.predict_proba(X_scaled)[0][1])
    rule_score = rule_based_risk_score(features)

    # Hybrid score: 60% ML + 40% rule-based
    final_prob = 0.6 * ml_prob + 0.4 * rule_score
    flag = int(final_prob >= 0.50)

    if final_prob < 0.35:
        risk_level = "Low"
    elif final_prob < 0.60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    shap_vals = get_shap_values(model, scaler, feature_vec, model_type)
    alerts = generate_alerts(features, final_prob)

    key_metrics = {
        "Debt-to-Equity": round(features["debt_to_equity"], 4),
        "Net Margin": round(features["net_margin"], 4),
        "ROA": round(features["roa"], 4),
        "Receivables/Revenue": round(features["receivables_to_revenue"], 4),
        "Cash Flow / Net Income": round(features["cash_flow_to_income"], 4),
        "Accruals Ratio": round(features["accruals"], 4),
        "Liabilities/Assets": round(features["liabilities_to_assets"], 4),
        "Operating Margin": round(features["op_margin"], 4),
    }

    return PredictionResponse(
        company_name=data.get("company_name", "Unknown"),
        manipulation_flag=flag,
        manipulation_probability=round(final_prob, 4),
        risk_level=risk_level,
        risk_score=round(final_prob * 100, 2),
        key_metrics=key_metrics,
        shap_values={k: round(v, 5) for k, v in shap_vals.items()},
        alerts=alerts,
    )

# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "Financial Risk Flagging System API is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/predict/manual", response_model=PredictionResponse)
def predict_manual(data: ManualInputData):
    """Predict financial manipulation risk from manually entered values."""
    payload = data.dict()
    model_type = payload.pop("model_type", "random_forest")
    try:
        result = predict_single(payload, model_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/csv")
async def predict_csv(file: UploadFile = File(...), model_type: str = "random_forest"):
    """Predict financial manipulation risk from an uploaded CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV parse error: {e}")

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    required = ["revenue", "net_income", "total_assets", "total_liabilities",
                "cash_flow_operations", "total_debt", "accounts_receivable", "equity"]
    missing = [r for r in required if r not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    results = []
    for _, row in df.iterrows():
        payload = row.to_dict()
        if "company_name" not in payload:
            payload["company_name"] = f"Company_{_}"
        result = predict_single(payload, model_type)
        results.append(result.dict())

    summary = {
        "total_companies": len(results),
        "flagged": sum(1 for r in results if r["manipulation_flag"] == 1),
        "high_risk": sum(1 for r in results if r["risk_level"] == "High"),
        "medium_risk": sum(1 for r in results if r["risk_level"] == "Medium"),
        "low_risk": sum(1 for r in results if r["risk_level"] == "Low"),
        "avg_risk_score": round(np.mean([r["risk_score"] for r in results]), 2),
    }
    return {"summary": summary, "results": results}


@app.get("/sample-csv-schema")
def sample_schema():
    """Returns the expected CSV schema with a sample row."""
    sample = {
        "company_name": "Acme Corp",
        "revenue": 5000000,
        "net_income": 300000,
        "total_assets": 8000000,
        "total_liabilities": 4500000,
        "cash_flow_operations": 250000,
        "total_debt": 2000000,
        "accounts_receivable": 800000,
        "equity": 3500000,
        "operating_income": 350000,
    }
    return {"schema": list(sample.keys()), "sample_row": sample}


@app.get("/feature-importance")
def feature_importance(model_type: str = "random_forest"):
    """Returns global feature importance from the trained model."""
    model, scaler = train_model(model_type)
    if model_type == "random_forest":
        importances = model.feature_importances_
    else:
        importances = np.abs(model.coef_[0])
        importances = importances / importances.sum()  # normalize
    return {
        "features": FEATURE_NAMES,
        "importances": [round(float(i), 5) for i in importances],
        "model_type": model_type,
    }
