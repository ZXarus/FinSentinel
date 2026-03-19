# 🏦 Bank-Grade Financial Risk Flagging System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SHAP](https://img.shields.io/badge/SHAP-Explainability-7C3AED?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**An ML-powered system to detect financial statement manipulation and earnings fraud using machine learning, SHAP explainability, and real-time risk scoring.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API Docs](#-api-endpoints) • [Team](#-team)

</div>

---

## 📌 Overview

Financial statement manipulation poses a serious risk to investors, banks, and regulatory bodies. Traditional audit mechanisms are often time-consuming and reactive — detecting issues only **after** substantial damage has occurred.

This system proactively identifies suspicious financial behavior using:
- **Machine Learning** (Random Forest + Logistic Regression)
- **SHAP Explainability** — understand *why* a company is flagged
- **Hybrid Scoring** — ML + rule-based financial heuristics
- **Real-time REST API** — built with FastAPI
- **Interactive Dashboard** — built with Streamlit

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔢 Manual Entry | Enter financial figures directly in the UI |
| 📂 CSV Batch Upload | Analyze dozens of companies at once |
| 🤖 Model Selection | Switch between Random Forest & Logistic Regression |
| 📊 SHAP Charts | See exactly which ratios triggered the risk flag |
| 🎯 Risk Classification | Low / Medium / High with probability score |
| 🚨 Smart Alerts | Plain-English explanations of each red flag |
| 📈 Radar Charts | Visual financial ratio profile per company |
| ⬇️ Export Results | Download batch analysis as CSV |
| 🌐 REST API | Full FastAPI backend with Swagger docs |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                    │
│   Manual Entry │ CSV Upload │ Feature Importance Tab    │
└────────────────────────┬────────────────────────────────┘
                         │  HTTP REST API
┌────────────────────────▼────────────────────────────────┐
│                     FASTAPI BACKEND                      │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Feature   │  │  ML Models   │  │     SHAP      │  │
│  │ Engineering │→ │  RF / LogReg │→ │ Explainability│  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Hybrid Scoring Engine                    │   │
│  │    60% ML Probability + 40% Rule-Based Score    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Financial Signals Detected

The system computes **9 derived financial ratios** from 8 raw inputs, based on the **Beneish M-Score** methodology:

| Signal | Formula | Red Flag Threshold |
|---|---|---|
| Accruals Ratio | (Net Income − CFO) / Assets | > 0.10 |
| Cash Flow / Income | CFO / Net Income | < 0.50 |
| Receivables / Revenue | Accounts Receivable / Revenue | > 0.30 |
| Debt-to-Equity | Total Debt / Equity | > 2.0 |
| ROA | Net Income / Total Assets | < 0 |
| Liabilities / Assets | Total Liabilities / Total Assets | > 0.80 |
| Operating Margin | Operating Income / Revenue | < 0 |
| Net Margin | Net Income / Revenue | Comparative |
| Asset Growth Ratio | (Assets − Liabilities) / Assets | Comparative |

> **Why only 8 inputs?** They are sufficient to derive all major manipulation signals. The Beneish M-Score — the gold standard in forensic accounting — also uses just 8 ratios.

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/financial-risk-flagging-system.git
cd financial-risk-flagging-system
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Start the backend
```bash
uvicorn backend:app --reload --port 8000
```

### Step 4 — Start the frontend (new terminal)
```bash
streamlit run frontend.py
```

App opens at: **http://localhost:8501**  
API Docs at: **http://localhost:8000/docs**

---

## 📋 Usage

### Option A — Manual Entry
1. Go to the **Manual Entry** tab
2. Enter company financial figures
3. Select model (Random Forest or Logistic Regression)
4. Click **Analyze Financial Risk**

### Option B — CSV Upload
1. Go to the **CSV Upload** tab
2. Upload a `.csv` file with the schema below
3. Click **Run Batch Analysis**
4. Drilldown into any company, download results

### CSV Schema
```
company_name, revenue, net_income, total_assets, total_liabilities,
cash_flow_operations, total_debt, accounts_receivable, equity, operating_income
```
Sample CSVs are included in the `sample_data/` folder.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API health check |
| `POST` | `/predict/manual` | Single company prediction |
| `POST` | `/predict/csv` | Batch CSV prediction |
| `GET` | `/feature-importance` | Model feature importance |
| `GET` | `/sample-csv-schema` | CSV schema + sample row |
| `GET` | `/docs` | Interactive Swagger UI |

### Example API Call
```python
import requests

payload = {
    "company_name": "Acme Corp",
    "revenue": 5000000,
    "net_income": 300000,
    "total_assets": 8000000,
    "total_liabilities": 4500000,
    "cash_flow_operations": 250000,
    "total_debt": 2000000,
    "accounts_receivable": 800000,
    "equity": 3500000,
    "model_type": "random_forest"
}

response = requests.post("http://localhost:8000/predict/manual", json=payload)
print(response.json())
```

### Example Response
```json
{
  "company_name": "Acme Corp",
  "manipulation_flag": 0,
  "manipulation_probability": 0.21,
  "risk_level": "Low",
  "risk_score": 21.4,
  "key_metrics": {
    "Debt-to-Equity": 0.571,
    "Net Margin": 0.060,
    "ROA": 0.037,
    "Accruals Ratio": 0.006
  },
  "alerts": ["✅ No major red flags detected"]
}
```

---

## 📁 Project Structure

```
financial-risk-flagging-system/
│
├── backend.py                   # FastAPI backend — ML + API logic
├── frontend.py                  # Streamlit frontend — UI
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Files excluded from Git
│
└── sample_data/
    ├── presentation_demo.csv    # Mixed demo — best for presentations
    ├── indian_companies_mix.csv # Indian companies (TCS, Infosys etc.)
    ├── all_clean_companies.csv  # All low-risk companies
    ├── all_high_risk.csv        # All high-risk/fraud companies
    ├── testing_borderline.csv   # Medium risk edge cases
    └── sample_companies.csv     # General testing
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, Matplotlib |
| Backend | FastAPI, Uvicorn |
| ML Models | Scikit-learn (Random Forest, Logistic Regression) |
| Explainability | SHAP |
| Data Processing | Pandas, NumPy |
| API Communication | REST / JSON |

---

## 👥 Team

| Name | Roll Number |
|---|---|
| P. Aryan | 23011M2211 |
| U. Adithya | 23011M2217 |
| M. Charan | 23011M2218 |

**Under the guidance of:** Ms. Praveena N  
**Program:** III B.Tech II Semester — CSE-IDDMP

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ for the love of clean financial books 📚
</div>
