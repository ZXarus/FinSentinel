"""
Bank-Grade Financial Risk Flagging System — Streamlit Frontend
Run: streamlit run frontend.py
Make sure backend.py is running: uvicorn backend:app --reload --port 8000
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import json
import base64
from pathlib import Path

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Risk Flagging System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

# ─────────────────────────────────────────────
# Custom CSS — Vibrant Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background: #0f0f1a; }

    /* Header gradient */
    .hero-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e94560;
        box-shadow: 0 0 40px rgba(233,69,96,0.2);
        text-align: center;
    }
    .hero-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-header p {
        color: #a0a8c0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    .hero-header .badge {
        display: inline-block;
        background: #e94560;
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 20px;
        margin-left: 10px;
        vertical-align: middle;
        letter-spacing: 1px;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-card.green { border-color: #00d4aa; }
    .metric-card.yellow { border-color: #ffd60a; }
    .metric-card.red { border-color: #e94560; }
    .metric-card h3 { color: #a0a8c0; font-size: 0.78rem; font-weight: 600;
                      text-transform: uppercase; letter-spacing: 1px; margin: 0; }
    .metric-card .value { font-size: 1.8rem; font-weight: 800; margin: 0.3rem 0 0; }
    .metric-card.green .value { color: #00d4aa; }
    .metric-card.yellow .value { color: #ffd60a; }
    .metric-card.red .value { color: #e94560; }

    /* Risk pill */
    .risk-pill {
        display: inline-block;
        padding: 6px 20px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
    }
    .risk-low { background: #00d4aa22; color: #00d4aa; border: 2px solid #00d4aa; }
    .risk-medium { background: #ffd60a22; color: #ffd60a; border: 2px solid #ffd60a; }
    .risk-high { background: #e9456022; color: #e94560; border: 2px solid #e94560; }

    /* Alert boxes */
    .alert-box {
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .alert-ok { background: #00d4aa15; border-left: 3px solid #00d4aa; color: #00d4aa; }
    .alert-warn { background: #ffd60a15; border-left: 3px solid #ffd60a; color: #ffd60a; }
    .alert-danger { background: #e9456015; border-left: 3px solid #e94560; color: #e94560; }

    /* Section header */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
        border-bottom: 2px solid #e94560;
        padding-bottom: 6px;
        margin: 1.5rem 0 1rem;
    }

    /* Results table */
    .results-table { border-radius: 10px; overflow: hidden; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid #2d2d50;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label { color: #a0a8c0 !important; }

    /* Input styling */
    .stNumberInput input, .stTextInput input {
        background: #1a1a2e !important;
        border: 1px solid #2d2d50 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #e94560 !important;
        box-shadow: 0 0 0 2px rgba(233,69,96,0.2) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #e94560, #c23152) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(233,69,96,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(233,69,96,0.5) !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #a0a8c0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #e94560 !important;
        color: white !important;
    }

    /* Upload area */
    .stFileUploader {
        border: 2px dashed #2d2d50;
        border-radius: 12px;
        background: #1a1a2e;
    }

    /* Divider */
    hr { border-color: #2d2d50; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def check_api():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except:
        return False


def color_for_risk(level):
    return {"Low": "green", "Medium": "yellow", "High": "red"}.get(level, "yellow")


def render_metric_card(title, value, color):
    st.markdown(
        f'<div class="metric-card {color}"><h3>{title}</h3><div class="value">{value}</div></div>',
        unsafe_allow_html=True
    )


def render_alert(text):
    if "✅" in text:
        cls = "alert-ok"
    elif "🚨" in text:
        cls = "alert-danger"
    else:
        cls = "alert-warn"
    st.markdown(f'<div class="alert-box {cls}">{text}</div>', unsafe_allow_html=True)


def gauge_chart(probability: float, risk_level: str):
    """Draw a half-circle gauge."""
    fig, ax = plt.subplots(figsize=(5, 2.8), subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor("#16213e")
    ax.set_facecolor("#16213e")

    # Zones
    colors = ["#00d4aa", "#ffd60a", "#e94560"]
    wedge_angles = [(180, 120), (120, 60), (60, 0)]
    for (start, end), c in zip(wedge_angles, colors):
        w = mpatches.Wedge((0, 0), 1.0, end, start, width=0.3,
                           facecolor=c, alpha=0.4, edgecolor="none")
        ax.add_patch(w)

    # Needle
    angle = (1 - probability) * 180
    rad = np.deg2rad(angle)
    ax.annotate("", xy=(0.75 * np.cos(rad), 0.75 * np.sin(rad)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2, mutation_scale=18))

    # Center text
    risk_colors = {"Low": "#00d4aa", "Medium": "#ffd60a", "High": "#e94560"}
    rc = risk_colors.get(risk_level, "white")
    ax.text(0, -0.25, f"{probability * 100:.1f}%", ha="center", va="center",
            fontsize=16, fontweight="bold", color=rc)
    ax.text(0, -0.5, risk_level.upper(), ha="center", va="center",
            fontsize=11, fontweight="bold", color=rc)

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.7, 1.2)
    ax.axis("off")
    plt.tight_layout(pad=0)
    return fig


def shap_bar_chart(shap_values: dict):
    """Horizontal SHAP importance bar chart."""
    items = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
    names = [i[0].replace("_", " ").title() for i in items]
    vals = [i[1] for i in items]
    colors = ["#e94560" if v > 0 else "#00d4aa" for v in vals]

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("#16213e")
    ax.set_facecolor("#16213e")
    bars = ax.barh(names[::-1], vals[::-1], color=colors[::-1], edgecolor="none", height=0.6)
    ax.axvline(0, color="#a0a8c0", linewidth=0.8, alpha=0.6)
    ax.set_xlabel("SHAP Value (Impact on Risk Score)", color="#a0a8c0", fontsize=9)
    ax.tick_params(colors="#a0a8c0", labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Feature Impact (SHAP)", color="#e2e8f0", fontsize=10, fontweight="bold", pad=10)

    red_patch = mpatches.Patch(color="#e94560", label="Increases Risk")
    green_patch = mpatches.Patch(color="#00d4aa", label="Decreases Risk")
    ax.legend(handles=[red_patch, green_patch], loc="lower right",
              facecolor="#1a1a2e", labelcolor="#a0a8c0", fontsize=8)
    plt.tight_layout()
    return fig


def metrics_radar(key_metrics: dict):
    """Radar chart of normalized key metrics."""
    labels = list(key_metrics.keys())[:7]
    raw_vals = [key_metrics[l] for l in labels]

    # Normalize to 0–1
    norm_vals = []
    for v in raw_vals:
        n = (v - (-1)) / (5 - (-1))
        norm_vals.append(max(0, min(1, n)))

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    norm_vals += norm_vals[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 4), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#16213e")
    ax.set_facecolor("#1a1a2e")
    ax.plot(angles, norm_vals, color="#e94560", linewidth=2)
    ax.fill(angles, norm_vals, color="#e94560", alpha=0.25)
    ax.set_xticks(angles[:-1])
    short_labels = [l[:12] for l in labels]
    ax.set_xticklabels(short_labels, fontsize=7.5, color="#a0a8c0")
    ax.set_yticklabels([])
    ax.set_title("Financial Ratios Profile", color="#e2e8f0", fontsize=10,
                 fontweight="bold", pad=20)
    ax.spines["polar"].set_color("#2d2d50")
    ax.grid(color="#2d2d50", linewidth=0.6)
    plt.tight_layout()
    return fig


def batch_summary_chart(results: list):
    """Stacked bar / pie summary for batch results."""
    counts = {"Low": 0, "Medium": 0, "High": 0}
    for r in results:
        counts[r["risk_level"]] = counts.get(r["risk_level"], 0) + 1

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor("#16213e")

    # Pie
    ax1 = axes[0]
    ax1.set_facecolor("#16213e")
    labels = [k for k, v in counts.items() if v > 0]
    sizes = [counts[k] for k in labels]
    colors_map = {"Low": "#00d4aa", "Medium": "#ffd60a", "High": "#e94560"}
    c = [colors_map[l] for l in labels]
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=c,
                                       autopct="%1.0f%%", startangle=90,
                                       textprops={"color": "#e2e8f0", "fontsize": 10})
    for at in autotexts:
        at.set_color("white")
        at.set_fontweight("bold")
    ax1.set_title("Risk Distribution", color="#e2e8f0", fontweight="bold", fontsize=11)

    # Risk score distribution
    ax2 = axes[1]
    ax2.set_facecolor("#16213e")
    scores = [r["risk_score"] for r in results]
    n, bins, patches = ax2.hist(scores, bins=12, edgecolor="#16213e")
    for patch, b in zip(patches, bins[:-1]):
        if b < 35:
            patch.set_facecolor("#00d4aa")
        elif b < 60:
            patch.set_facecolor("#ffd60a")
        else:
            patch.set_facecolor("#e94560")
    ax2.set_xlabel("Risk Score", color="#a0a8c0", fontsize=9)
    ax2.set_ylabel("Count", color="#a0a8c0", fontsize=9)
    ax2.set_title("Risk Score Distribution", color="#e2e8f0", fontweight="bold", fontsize=11)
    ax2.tick_params(colors="#a0a8c0")
    for spine in ax2.spines.values():
        spine.set_edgecolor("#2d2d50")
    ax2.set_facecolor("#16213e")

    plt.tight_layout()
    return fig


def show_result_panel(result: dict):
    """Render a complete result panel for a single prediction."""
    risk = result["risk_level"]
    color = color_for_risk(risk)
    prob = result["manipulation_probability"]

    st.markdown('<div class="section-title">📊 Risk Assessment</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Manipulation Flag",
                           "🚨 FLAGGED" if result["manipulation_flag"] else "✅ CLEAN",
                           "red" if result["manipulation_flag"] else "green")
    with col2:
        render_metric_card("Risk Score", f"{result['risk_score']:.1f}/100", color)
    with col3:
        render_metric_card("Risk Level", risk, color)

    col_g, col_r = st.columns([1, 1])
    with col_g:
        st.pyplot(gauge_chart(prob, risk), use_container_width=True)
    with col_r:
        st.markdown('<div class="section-title">🔔 Alerts</div>', unsafe_allow_html=True)
        for alert in result["alerts"]:
            render_alert(alert)

    st.markdown('<div class="section-title">📈 Financial Metrics</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (k, v) in enumerate(result["key_metrics"].items()):
        with cols[i % 4]:
            threshold_color = "green" if abs(v) < 0.5 else ("yellow" if abs(v) < 1.5 else "red")
            render_metric_card(k, f"{v:.4f}", threshold_color)

    if result.get("shap_values"):
        st.markdown('<div class="section-title">🔍 SHAP Explainability</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns([3, 2])
        with col_s1:
            st.pyplot(shap_bar_chart(result["shap_values"]), use_container_width=True)
        with col_s2:
            st.pyplot(metrics_radar(result["key_metrics"]), use_container_width=True)

    with st.expander("📋 Raw JSON Result"):
        st.json(result)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem'>🏦</div>
        <div style='color:#e2e8f0; font-weight:800; font-size:1rem;'>FINANCIAL RISK SYSTEM</div>
        <div style='color:#a0a8c0; font-size:0.75rem;'>Bank-Grade Detection Engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    api_alive = check_api()
    if api_alive:
        st.markdown("""<div style='background:#00d4aa22;border:1px solid #00d4aa;border-radius:8px;
        padding:8px 12px;color:#00d4aa;font-weight:600;font-size:0.85rem;'>
        🟢 API Connected</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='background:#e9456022;border:1px solid #e94560;border-radius:8px;
        padding:8px 12px;color:#e94560;font-weight:600;font-size:0.85rem;'>
        🔴 API Offline — Start backend first</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="color:#a0a8c0;font-weight:700;font-size:0.85rem;margin-bottom:8px;">⚙️ MODEL SELECTION</div>', unsafe_allow_html=True)
    model_type = st.radio(
        "",
        ["Random Forest", "Logistic Regression"],
        index=0,
    )
    model_key = "random_forest" if "Random" in model_type else "linear_regression"

    st.markdown("---")
    st.markdown("""
    <div style='color:#a0a8c0;font-size:0.78rem;line-height:1.6;'>
    <b style='color:#e2e8f0;'>Key Signals Detected:</b><br>
    • High accruals ratio<br>
    • Cash flow vs income gap<br>
    • Excessive receivables<br>
    • High debt-to-equity<br>
    • Negative ROA<br>
    • Liabilities > 80% assets<br><br>
    <b style='color:#e2e8f0;'>Risk Levels:</b><br>
    🟢 Low: 0–35%<br>
    🟡 Medium: 35–60%<br>
    🔴 High: 60–100%
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main Header
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <h1>🏦 Bank-Grade Financial Risk Flagging System
        <span class="badge">ML + SHAP</span>
    </h1>
    <p>Detect earnings manipulation & financial fraud using machine learning and SHAP explainability</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    "  🔢  Manual Entry  ",
    "  📂  CSV Upload  ",
    "  📊  Feature Importance  ",
])

# ═══════════════════════════════
# TAB 1 — Manual Input
# ═══════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📝 Enter Company Financial Data</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#a0a8c0;font-size:0.85rem;margin-bottom:1rem;">All monetary values can be in any consistent currency unit (e.g., USD thousands).</div>', unsafe_allow_html=True)

    company_name = st.text_input("🏢 Company Name", value="Acme Corp", placeholder="Enter company name...")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        revenue = st.number_input("💰 Revenue", value=5_000_000.0, step=100_000.0, format="%.2f",
                                   help="Total annual revenue")
        net_income = st.number_input("📈 Net Income", value=300_000.0, step=10_000.0, format="%.2f",
                                      help="Net profit after tax")
        total_assets = st.number_input("🏗️ Total Assets", value=8_000_000.0, step=100_000.0, format="%.2f")
        accounts_receivable = st.number_input("📋 Accounts Receivable", value=800_000.0, step=10_000.0, format="%.2f",
                                               help="Outstanding customer payments")

    with col2:
        total_liabilities = st.number_input("💳 Total Liabilities", value=4_500_000.0, step=100_000.0, format="%.2f")
        cash_flow_operations = st.number_input("🔄 Cash Flow from Operations", value=250_000.0, step=10_000.0, format="%.2f",
                                                help="Operating cash flow (can be negative)")
        total_debt = st.number_input("🏦 Total Debt", value=2_000_000.0, step=50_000.0, format="%.2f")
        equity = st.number_input("📊 Equity (Shareholders)", value=3_500_000.0, step=50_000.0, format="%.2f")

    operating_income = st.number_input("⚙️ Operating Income (optional)", value=350_000.0,
                                        step=10_000.0, format="%.2f")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Analyze Financial Risk", key="manual_btn"):
        if not api_alive:
            st.error("❌ Backend API is not running. Please start the backend with: `uvicorn backend:app --reload --port 8000`")
        else:
            with st.spinner("🧠 Running ML analysis + SHAP explanation..."):
                payload = {
                    "company_name": company_name,
                    "revenue": revenue,
                    "net_income": net_income,
                    "total_assets": total_assets,
                    "total_liabilities": total_liabilities,
                    "cash_flow_operations": cash_flow_operations,
                    "total_debt": total_debt,
                    "accounts_receivable": accounts_receivable,
                    "equity": equity,
                    "operating_income": operating_income,
                    "model_type": model_key,
                }
                try:
                    response = requests.post(f"{API_URL}/predict/manual", json=payload, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Analysis complete for **{company_name}**")
                        show_result_panel(result)
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")


# ═══════════════════════════════
# TAB 2 — CSV Upload
# ═══════════════════════════════
with tab2:
    st.markdown('<div class="section-title">📂 Upload CSV for Batch Analysis</div>', unsafe_allow_html=True)

    # Show schema helper
    with st.expander("📋 Required CSV Schema & Sample"):
        sample_df = pd.DataFrame([
            {
                "company_name": "Acme Corp", "revenue": 5000000, "net_income": 300000,
                "total_assets": 8000000, "total_liabilities": 4500000,
                "cash_flow_operations": 250000, "total_debt": 2000000,
                "accounts_receivable": 800000, "equity": 3500000, "operating_income": 350000,
            },
            {
                "company_name": "RiskyBiz Ltd", "revenue": 2000000, "net_income": 400000,
                "total_assets": 9000000, "total_liabilities": 8500000,
                "cash_flow_operations": -50000, "total_debt": 7000000,
                "accounts_receivable": 1500000, "equity": 500000, "operating_income": 350000,
            },
        ])
        st.dataframe(sample_df, use_container_width=True)

        # Provide download button for sample CSV
        csv_bytes = sample_df.to_csv(index=False).encode()
        st.download_button("⬇️ Download Sample CSV", csv_bytes,
                           file_name="sample_financial_data.csv", mime="text/csv")

    uploaded_file = st.file_uploader(
        "Drop your CSV here or click to browse",
        type=["csv"],
        help="Must contain: revenue, net_income, total_assets, total_liabilities, cash_flow_operations, total_debt, accounts_receivable, equity"
    )

    if uploaded_file:
        try:
            preview_df = pd.read_csv(uploaded_file)
            st.markdown(f'<div style="color:#a0a8c0;font-size:0.85rem;">📄 {len(preview_df)} rows × {len(preview_df.columns)} columns detected</div>', unsafe_allow_html=True)
            with st.expander("👁️ Preview Data"):
                st.dataframe(preview_df.head(10), use_container_width=True)
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Preview error: {e}")

        if st.button("🚀 Run Batch Analysis", key="csv_btn"):
            if not api_alive:
                st.error("❌ Backend API is not running.")
            else:
                with st.spinner("🔄 Analyzing all companies..."):
                    try:
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file.read(), "text/csv")}
                        response = requests.post(
                            f"{API_URL}/predict/csv",
                            files=files,
                            params={"model_type": model_key},
                            timeout=120
                        )
                        if response.status_code == 200:
                            data = response.json()
                            summary = data["summary"]
                            results = data["results"]

                            st.success(f"✅ Analyzed **{summary['total_companies']}** companies")

                            # Summary metrics
                            st.markdown('<div class="section-title">📊 Batch Summary</div>', unsafe_allow_html=True)
                            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                            with mc1:
                                render_metric_card("Total Companies", summary["total_companies"], "green")
                            with mc2:
                                render_metric_card("Flagged", summary["flagged"], "red" if summary["flagged"] > 0 else "green")
                            with mc3:
                                render_metric_card("High Risk", summary["high_risk"], "red")
                            with mc4:
                                render_metric_card("Medium Risk", summary["medium_risk"], "yellow")
                            with mc5:
                                render_metric_card("Avg Risk Score", f"{summary['avg_risk_score']:.1f}", "yellow")

                            # Charts
                            st.pyplot(batch_summary_chart(results), use_container_width=True)

                            # Results table
                            st.markdown('<div class="section-title">📋 Company Results</div>', unsafe_allow_html=True)
                            table_data = []
                            for r in results:
                                table_data.append({
                                    "Company": r["company_name"],
                                    "Flag": "🚨 YES" if r["manipulation_flag"] else "✅ NO",
                                    "Risk Level": r["risk_level"],
                                    "Risk Score": f"{r['risk_score']:.1f}",
                                    "Probability": f"{r['manipulation_probability']*100:.1f}%",
                                    "Top Alert": r["alerts"][0] if r["alerts"] else "",
                                })
                            table_df = pd.DataFrame(table_data)
                            st.dataframe(table_df, use_container_width=True, height=350)

                            # Download results
                            results_csv = pd.DataFrame([{
                                "company": r["company_name"],
                                "flag": r["manipulation_flag"],
                                "risk_level": r["risk_level"],
                                "risk_score": r["risk_score"],
                                "probability": r["manipulation_probability"],
                            } for r in results]).to_csv(index=False).encode()
                            st.download_button("⬇️ Download Results CSV", results_csv,
                                               file_name="risk_analysis_results.csv", mime="text/csv")

                            # Drilldown
                            st.markdown('<div class="section-title">🔍 Company Deep-Dive</div>', unsafe_allow_html=True)
                            company_names = [r["company_name"] for r in results]
                            selected = st.selectbox("Select a company to inspect:", company_names)
                            selected_result = next(r for r in results if r["company_name"] == selected)
                            show_result_panel(selected_result)

                        else:
                            st.error(f"API Error {response.status_code}: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")


# ═══════════════════════════════
# TAB 3 — Feature Importance
# ═══════════════════════════════
with tab3:
    st.markdown('<div class="section-title">🌟 Global Feature Importance</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#a0a8c0;font-size:0.85rem;margin-bottom:1rem;">Which financial ratios contribute most to predicting manipulation risk?</div>', unsafe_allow_html=True)

    if st.button("📊 Load Feature Importance", key="fi_btn"):
        if not api_alive:
            st.error("❌ Backend API is not running.")
        else:
            with st.spinner("Loading model insights..."):
                try:
                    resp = requests.get(f"{API_URL}/feature-importance",
                                        params={"model_type": model_key}, timeout=30)
                    if resp.status_code == 200:
                        fi_data = resp.json()
                        features = fi_data["features"]
                        importances = fi_data["importances"]

                        pairs = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)
                        f_sorted = [p[0].replace("_", " ").title() for p in pairs]
                        i_sorted = [p[1] for p in pairs]

                        fig, ax = plt.subplots(figsize=(8, 5))
                        fig.patch.set_facecolor("#16213e")
                        ax.set_facecolor("#16213e")

                        gradient_colors = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(f_sorted)))
                        bars = ax.barh(f_sorted[::-1], i_sorted[::-1], color=gradient_colors,
                                       edgecolor="none", height=0.65)

                        for bar, val in zip(bars, i_sorted[::-1]):
                            ax.text(val + 0.003, bar.get_y() + bar.get_height() / 2,
                                    f"{val:.3f}", va="center", color="#e2e8f0", fontsize=9)

                        ax.set_xlabel("Importance Score", color="#a0a8c0", fontsize=10)
                        ax.set_title(f"Feature Importance — {fi_data['model_type'].replace('_',' ').title()}",
                                     color="#e2e8f0", fontsize=13, fontweight="bold", pad=15)
                        ax.tick_params(colors="#a0a8c0")
                        for spine in ax.spines.values():
                            spine.set_visible(False)
                        plt.tight_layout()
                        st.pyplot(fig, use_container_width=True)

                        # Table
                        fi_df = pd.DataFrame({"Feature": f_sorted, "Importance": i_sorted})
                        fi_df["Rank"] = range(1, len(fi_df) + 1)
                        fi_df = fi_df[["Rank", "Feature", "Importance"]]
                        st.dataframe(fi_df, use_container_width=True, hide_index=True)

                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("""
    <div style='background:#1a1a2e;border-radius:12px;padding:1.5rem;border:1px solid #2d2d50;'>
    <div style='color:#e2e8f0;font-weight:700;font-size:1rem;margin-bottom:1rem;'>📚 About the Financial Signals</div>
    <table style='width:100%;color:#a0a8c0;font-size:0.85rem;border-collapse:collapse;'>
    <tr style='border-bottom:1px solid #2d2d50;'>
        <th style='text-align:left;padding:6px;color:#e2e8f0;'>Signal</th>
        <th style='text-align:left;padding:6px;color:#e2e8f0;'>Formula</th>
        <th style='text-align:left;padding:6px;color:#e2e8f0;'>Red Flag Threshold</th>
    </tr>
    <tr style='border-bottom:1px solid #1a1a2e;'>
        <td style='padding:6px;'>Accruals Ratio</td>
        <td style='padding:6px;'>(Net Income − CFO) / Assets</td>
        <td style='padding:6px;color:#e94560;'>&gt; 0.10</td>
    </tr>
    <tr style='border-bottom:1px solid #1a1a2e;'>
        <td style='padding:6px;'>Cash Flow / Income</td>
        <td style='padding:6px;'>CFO / Net Income</td>
        <td style='padding:6px;color:#e94560;'>&lt; 0.50</td>
    </tr>
    <tr style='border-bottom:1px solid #1a1a2e;'>
        <td style='padding:6px;'>Receivables/Revenue</td>
        <td style='padding:6px;'>Accounts Receivable / Revenue</td>
        <td style='padding:6px;color:#e94560;'>&gt; 0.30</td>
    </tr>
    <tr style='border-bottom:1px solid #1a1a2e;'>
        <td style='padding:6px;'>Debt-to-Equity</td>
        <td style='padding:6px;'>Total Debt / Equity</td>
        <td style='padding:6px;color:#e94560;'>&gt; 2.0</td>
    </tr>
    <tr style='border-bottom:1px solid #1a1a2e;'>
        <td style='padding:6px;'>Liabilities/Assets</td>
        <td style='padding:6px;'>Total Liabilities / Total Assets</td>
        <td style='padding:6px;color:#e94560;'>&gt; 0.80</td>
    </tr>
    <tr>
        <td style='padding:6px;'>ROA</td>
        <td style='padding:6px;'>Net Income / Total Assets</td>
        <td style='padding:6px;color:#e94560;'>&lt; 0</td>
    </tr>
    </table>
    </div>
    """, unsafe_allow_html=True)
