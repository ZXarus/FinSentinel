import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io

API_URL = "http://localhost:8000"

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FinSentinel",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Deploy button, hamburger menu, footer */
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden !important; }

    /* Main background — soft warm off-white */
    .main, .block-container {
        background: #f5f7fa !important;
    }
    [data-testid="stAppViewContainer"] {
        background: #f5f7fa !important;
    }
    [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }

    /* Hero header */
    .hero-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #1a4a7a 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        border: none;
        box-shadow: 0 8px 32px rgba(30,58,95,0.18);
        text-align: center;
    }
    .hero-header h1 {
        color: #ffffff;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-header p {
        color: #b8cce4;
        font-size: 0.98rem;
        margin-top: 0.5rem;
    }
    .hero-header .badge {
        display: inline-block;
        background: #e94560;
        color: white;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 20px;
        margin-left: 10px;
        vertical-align: middle;
        letter-spacing: 1px;
    }

    /* Metric cards — white with coloured left border */
    .metric-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.1rem 1.4rem;
        border-left: 4px solid;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    }
    .metric-card.green  { border-color: #10b981; }
    .metric-card.yellow { border-color: #f59e0b; }
    .metric-card.red    { border-color: #ef4444; }
    .metric-card h3 {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
    }
    .metric-card .value { font-size: 1.7rem; font-weight: 800; margin: 0.3rem 0 0; }
    .metric-card.green  .value { color: #10b981; }
    .metric-card.yellow .value { color: #f59e0b; }
    .metric-card.red    .value { color: #ef4444; }

    /* Alert boxes */
    .alert-box {
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.88rem;
        font-weight: 500;
    }
    .alert-ok     { background: #ecfdf5; border-left: 3px solid #10b981; color: #065f46; }
    .alert-warn   { background: #fffbeb; border-left: 3px solid #f59e0b; color: #92400e; }
    .alert-danger { background: #fef2f2; border-left: 3px solid #ef4444; color: #991b1b; }

    /* Section title */
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e3a5f;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 6px;
        margin: 1.5rem 0 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #1a4a7a 100%) !important;
        border-right: none;
    }
    section[data-testid="stSidebar"] * { color: #e2eaf4 !important; }
    section[data-testid="stSidebar"] .stRadio label { color: #b8cce4 !important; }

    /* Input fields — clean white */
    .stNumberInput input, .stTextInput input {
        background: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        color: #1e293b !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }

    /* Fix — + stepper buttons on number inputs */
    .stNumberInput button {
        background: #e8edf5 !important;
        border: 1px solid #cbd5e1 !important;
        color: #1e3a5f !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    .stNumberInput button:hover {
        background: #3b82f6 !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
    }
    .stNumberInput button p, .stNumberInput button span {
        color: #1e3a5f !important;
    }

    /* Fix all labels — make them clearly visible */
    label, .stTextInput label, .stNumberInput label,
    .stSelectbox label, .stRadio label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] {
        color: #1e3a5f !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        opacity: 1 !important;
    }

    /* Fix emoji icons next to labels */
    [data-testid="stWidgetLabel"] p {
        color: #1e3a5f !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }

    /* General text color fix for main area */
    .main p, .main span, .main div {
        color: #1e293b;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        letter-spacing: 0.4px !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(37,99,235,0.45) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #e8edf5;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #475569;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background: #1e3a5f !important;
        color: white !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 2px dashed #94a3b8;
        border-radius: 12px;
        padding: 1rem;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        border-radius: 8px !important;
        color: #1e3a5f !important;
        font-weight: 600 !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] { background: #ffffff; border-radius: 10px; }

    hr { border-color: #e2e8f0; }

    /* Selectbox visible box */
    .stSelectbox [data-baseweb="select"] > div:first-child {
        background: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    /* Text inside visible box */
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {
        color: #1e293b !important;
        background: #ffffff !important;
    }
    /* Dropdown panel */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    ul[data-baseweb="menu"] {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
    }
    /* Each option */
    [role="option"], li[role="option"] {
        background: #ffffff !important;
        color: #1e293b !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    /* Hovered option */
    [role="option"]:hover, li[role="option"]:hover {
        background: #eff6ff !important;
        color: #1e3a5f !important;
    }
    /* Selected option */
    [aria-selected="true"][role="option"] {
        background: #dbeafe !important;
        color: #1e3a5f !important;
        font-weight: 700 !important;
    }
    /* Dropdown arrow */
    .stSelectbox svg { fill: #1e3a5f !important; }
    /* Selectbox label */
    .stSelectbox label { color: #1e3a5f !important; font-weight: 600 !important; }

            /* Force all button text to white, including blue buttons */
.stButton > button,
.stButton > button * {
    color: #fff !important;
    fill: #fff !important;
}
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


def gauge_chart(probability, risk_level):
    fig, ax = plt.subplots(figsize=(5, 2.8), subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    colors = ["#10b981", "#f59e0b", "#ef4444"]
    wedge_angles = [(180, 120), (120, 60), (60, 0)]
    for (start, end), c in zip(wedge_angles, colors):
        w = mpatches.Wedge((0, 0), 1.0, end, start, width=0.3,
                           facecolor=c, alpha=0.35, edgecolor="none")
        ax.add_patch(w)

    angle = (1 - probability) * 180
    rad = np.deg2rad(angle)
    ax.annotate("", xy=(0.75 * np.cos(rad), 0.75 * np.sin(rad)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="#1e3a5f", lw=2.5, mutation_scale=18))

    risk_colors = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
    rc = risk_colors.get(risk_level, "#1e3a5f")
    ax.text(0, -0.25, f"{probability * 100:.1f}%", ha="center", va="center",
            fontsize=17, fontweight="bold", color=rc)
    ax.text(0, -0.52, risk_level.upper(), ha="center", va="center",
            fontsize=11, fontweight="bold", color=rc)

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.7, 1.2)
    ax.axis("off")
    plt.tight_layout(pad=0)
    return fig


def shap_bar_chart(shap_values):
    items = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
    names = [i[0].replace("_", " ").title() for i in items]
    vals  = [i[1] for i in items]
    colors = ["#ef4444" if v > 0 else "#10b981" for v in vals]

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    ax.barh(names[::-1], vals[::-1], color=colors[::-1], edgecolor="none", height=0.6)
    ax.axvline(0, color="#94a3b8", linewidth=0.8)
    ax.set_xlabel("SHAP Value (Impact on Risk Score)", color="#475569", fontsize=9)
    ax.tick_params(colors="#475569", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#e2e8f0")
    ax.set_title("Feature Impact (SHAP)", color="#1e3a5f", fontsize=10, fontweight="bold", pad=10)
    red_p   = mpatches.Patch(color="#ef4444", label="Increases Risk")
    green_p = mpatches.Patch(color="#10b981", label="Decreases Risk")
    ax.legend(handles=[red_p, green_p], loc="lower right",
              facecolor="#ffffff", labelcolor="#475569", fontsize=8)
    plt.tight_layout()
    return fig


def metrics_radar(key_metrics):
    labels = list(key_metrics.keys())[:7]
    raw_vals = [key_metrics[l] for l in labels]
    norm_vals = [max(0, min(1, (v + 1) / 6)) for v in raw_vals]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    norm_vals += norm_vals[:1]
    angles    += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 4), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    ax.plot(angles, norm_vals, color="#2563eb", linewidth=2)
    ax.fill(angles, norm_vals, color="#2563eb", alpha=0.18)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([l[:12] for l in labels], fontsize=7.5, color="#475569")
    ax.set_yticklabels([])
    ax.set_title("Financial Ratios Profile", color="#1e3a5f", fontsize=10,
                 fontweight="bold", pad=20)
    ax.spines["polar"].set_color("#e2e8f0")
    ax.grid(color="#cbd5e1", linewidth=0.6)
    plt.tight_layout()
    return fig


def batch_summary_chart(results):
    counts = {"Low": 0, "Medium": 0, "High": 0}
    for r in results:
        counts[r["risk_level"]] = counts.get(r["risk_level"], 0) + 1

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor("#ffffff")

    ax1 = axes[0]
    ax1.set_facecolor("#ffffff")
    labels = [k for k, v in counts.items() if v > 0]
    sizes  = [counts[k] for k in labels]
    cmap   = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
    c = [cmap[l] for l in labels]
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=c,
                                       autopct="%1.0f%%", startangle=90,
                                       textprops={"color": "#1e293b", "fontsize": 10})
    for at in autotexts:
        at.set_fontweight("bold")
    ax1.set_title("Risk Distribution", color="#1e3a5f", fontweight="bold", fontsize=11)

    ax2 = axes[1]
    ax2.set_facecolor("#f8fafc")
    scores = [r["risk_score"] for r in results]
    n, bins, patches = ax2.hist(scores, bins=12, edgecolor="#ffffff")
    for patch, b in zip(patches, bins[:-1]):
        patch.set_facecolor("#10b981" if b < 35 else ("#f59e0b" if b < 60 else "#ef4444"))
    ax2.set_xlabel("Risk Score", color="#475569", fontsize=9)
    ax2.set_ylabel("Count",      color="#475569", fontsize=9)
    ax2.set_title("Risk Score Distribution", color="#1e3a5f", fontweight="bold", fontsize=11)
    ax2.tick_params(colors="#475569")
    for spine in ax2.spines.values():
        spine.set_edgecolor("#e2e8f0")
    plt.tight_layout()
    return fig


def show_result_panel(result):
    risk  = result["risk_level"]
    color = color_for_risk(risk)
    prob  = result["manipulation_probability"]

    st.markdown('<div class="section-title">📊 Risk Assessment</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Manipulation Flag",
                           "🚨 FLAGGED" if result["manipulation_flag"] else "✅ CLEAN",
                           "red" if result["manipulation_flag"] else "green")
    with c2:
        render_metric_card("Risk Score", f"{result['risk_score']:.1f}/100", color)
    with c3:
        render_metric_card("Risk Level", risk, color)

    cg, cr = st.columns([1, 1])
    with cg:
        st.pyplot(gauge_chart(prob, risk), use_container_width=True)
    with cr:
        st.markdown('<div class="section-title">🔔 Alerts</div>', unsafe_allow_html=True)
        for alert in result["alerts"]:
            render_alert(alert)

    st.markdown('<div class="section-title">📈 Financial Metrics</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (k, v) in enumerate(result["key_metrics"].items()):
        with cols[i % 4]:
            tc = "green" if abs(v) < 0.5 else ("yellow" if abs(v) < 1.5 else "red")
            render_metric_card(k, f"{v:.4f}", tc)

    if result.get("shap_values"):
        st.markdown('<div class="section-title">🔍 SHAP Explainability</div>', unsafe_allow_html=True)
        s1, s2 = st.columns([3, 2])
        with s1:
            st.pyplot(shap_bar_chart(result["shap_values"]), use_container_width=True)
        with s2:
            st.pyplot(metrics_radar(result["key_metrics"]), use_container_width=True)

    with st.expander("📋 Raw JSON Result"):
        st.json(result)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 0.5rem;'>
        <div style='font-size:2.8rem;'>🏦</div>
        <div style='color:#ffffff;font-weight:800;font-size:1.05rem;letter-spacing:0.5px;'>FinSentinel</div>
        <div style='color:#93b4d4;font-size:0.75rem;margin-top:2px;'>Bank-Grade Detection Engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    api_alive = check_api()
    if api_alive:
        st.markdown("""<div style='background:rgba(16,185,129,0.2);border:1px solid #10b981;
        border-radius:8px;padding:8px 12px;color:#6ee7b7;font-weight:600;font-size:0.85rem;'>
        🟢 API Connected</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='background:rgba(239,68,68,0.2);border:1px solid #ef4444;
        border-radius:8px;padding:8px 12px;color:#fca5a5;font-weight:600;font-size:0.85rem;'>
        🔴 API Offline<br><span style='font-size:0.75rem;font-weight:400;'>Run: uvicorn backend:app --port 8000</span></div>""",
        unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="color:#93b4d4;font-weight:700;font-size:0.82rem;margin-bottom:8px;">⚙️ MODEL SELECTION</div>',
                unsafe_allow_html=True)
    model_type = st.radio("", ["Random Forest", "Logistic Regression"], index=0)
    model_key  = "random_forest" if "Random" in model_type else "linear_regression"

    st.markdown("---")
    st.markdown("""
    <div style='color:#93b4d4;font-size:0.78rem;line-height:1.8;'>
    <b style='color:#ffffff;'>Key Signals Detected:</b><br>
    • High accruals ratio<br>
    • Cash flow vs income gap<br>
    • Excessive receivables<br>
    • High debt-to-equity<br>
    • Negative ROA<br>
    • Liabilities &gt; 80% assets<br><br>
    <b style='color:#ffffff;'>Risk Levels:</b><br>
    🟢 Low &nbsp;&nbsp;: 0 – 35%<br>
    🟡 Medium: 35 – 60%<br>
    🔴 High &nbsp;: 60 – 100%
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1><span style="color:#fff;">🏦 FinSentinel</span> <span class="badge">ML + SHAP</span></h1>
    <p style="color:#fff;">Bank-Grade Earnings Manipulation Detector — powered by Machine Learning & Explainable AI</p>
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

# ══════════════════════════════
# TAB 1 — Manual Entry
# ══════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📝 Enter Company Financial Data</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;font-size:0.85rem;margin-bottom:1rem;">All monetary values in any consistent unit (e.g. USD, INR thousands).</div>',
                unsafe_allow_html=True)

    company_name = st.text_input("🏢 Company Name", value="Acme Corp")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        revenue               = st.number_input("💰 Revenue",                  value=5_000_000.0, step=100_000.0, format="%.2f")
        net_income            = st.number_input("📈 Net Income",                value=300_000.0,   step=10_000.0,  format="%.2f")
        total_assets          = st.number_input("🏗️ Total Assets",              value=8_000_000.0, step=100_000.0, format="%.2f")
        accounts_receivable   = st.number_input("📋 Accounts Receivable",       value=800_000.0,   step=10_000.0,  format="%.2f")
    with c2:
        total_liabilities     = st.number_input("💳 Total Liabilities",         value=4_500_000.0, step=100_000.0, format="%.2f")
        cash_flow_operations  = st.number_input("🔄 Cash Flow from Operations", value=250_000.0,   step=10_000.0,  format="%.2f")
        total_debt            = st.number_input("🏦 Total Debt",                value=2_000_000.0, step=50_000.0,  format="%.2f")
        equity                = st.number_input("📊 Equity (Shareholders)",     value=3_500_000.0, step=50_000.0,  format="%.2f")

    operating_income = st.number_input("⚙️ Operating Income (optional)", value=350_000.0, step=10_000.0, format="%.2f")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Analyze Financial Risk", key="manual_btn"):
        if not api_alive:
            st.error("❌ Backend API not running. Start it with: uvicorn backend:app --reload --port 8000")
        else:
            with st.spinner("🧠 Running ML analysis + SHAP explanation..."):
                payload = {
                    "company_name": company_name, "revenue": revenue,
                    "net_income": net_income, "total_assets": total_assets,
                    "total_liabilities": total_liabilities,
                    "cash_flow_operations": cash_flow_operations,
                    "total_debt": total_debt, "accounts_receivable": accounts_receivable,
                    "equity": equity, "operating_income": operating_income,
                    "model_type": model_key,
                }
                try:
                    resp = requests.post(f"{API_URL}/predict/manual", json=payload, timeout=30)
                    if resp.status_code == 200:
                        result = resp.json()
                        st.success(f"✅ Analysis complete for **{company_name}**")
                        show_result_panel(result)
                    else:
                        st.error(f"API Error {resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")


# ══════════════════════════════
# TAB 2 — CSV Upload
# ══════════════════════════════

# Store batch results in session state so drilldown works after rerun
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None

with tab2:
    st.markdown('<div class="section-title">📂 Batch Analysis via CSV Upload</div>', unsafe_allow_html=True)

    with st.expander("📋 Required CSV Schema & Sample Download"):
        sample_df = pd.DataFrame([
            {"company_name":"Acme Corp","revenue":5000000,"net_income":300000,
             "total_assets":8000000,"total_liabilities":4500000,"cash_flow_operations":250000,
             "total_debt":2000000,"accounts_receivable":800000,"equity":3500000,"operating_income":350000},
            {"company_name":"RiskyBiz Ltd","revenue":2000000,"net_income":400000,
             "total_assets":9000000,"total_liabilities":8500000,"cash_flow_operations":-50000,
             "total_debt":7000000,"accounts_receivable":1500000,"equity":500000,"operating_income":200000},
        ])
        st.dataframe(sample_df, use_container_width=True)
        st.download_button("⬇️ Download Sample CSV",
                           sample_df.to_csv(index=False).encode(),
                           file_name="sample_financial_data.csv", mime="text/csv")

    uploaded_file = st.file_uploader(
        "Drop your CSV here or click to browse",
        type=["csv"],
        help="Columns needed: revenue, net_income, total_assets, total_liabilities, cash_flow_operations, total_debt, accounts_receivable, equity"
    )

    if uploaded_file:
        try:
            preview_df = pd.read_csv(uploaded_file)
            st.info(f"📄 **{len(preview_df)} rows** × **{len(preview_df.columns)} columns** detected")
            with st.expander("👁️ Preview Uploaded Data"):
                st.dataframe(preview_df.head(10), use_container_width=True)
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Preview error: {e}")

        if st.button("🚀 Run Batch Analysis", key="csv_btn"):
            if not api_alive:
                st.error("❌ Backend API not running.")
            else:
                with st.spinner("🔄 Analyzing all companies..."):
                    try:
                        uploaded_file.seek(0)
                        files    = {"file": (uploaded_file.name, uploaded_file.read(), "text/csv")}
                        response = requests.post(f"{API_URL}/predict/csv", files=files,
                                                 params={"model_type": model_key}, timeout=120)
                        if response.status_code == 200:
                            data    = response.json()
                            summary = data["summary"]
                            results = data["results"]
                            # Store in session state so drilldown works after selectbox rerun
                            st.session_state.batch_results = results

                            st.success(f"✅ Analyzed **{summary['total_companies']}** companies")

                            st.markdown('<div class="section-title">📊 Batch Summary</div>', unsafe_allow_html=True)
                            m1, m2, m3, m4, m5 = st.columns(5)
                            with m1: render_metric_card("Total",       summary["total_companies"],         "green")
                            with m2: render_metric_card("Flagged",     summary["flagged"],                 "red" if summary["flagged"] else "green")
                            with m3: render_metric_card("High Risk",   summary["high_risk"],               "red")
                            with m4: render_metric_card("Medium Risk", summary["medium_risk"],             "yellow")
                            with m5: render_metric_card("Avg Score",   f"{summary['avg_risk_score']:.1f}", "yellow")

                            st.pyplot(batch_summary_chart(results), use_container_width=True)

                            st.markdown('<div class="section-title">📋 All Companies</div>', unsafe_allow_html=True)
                            table_df = pd.DataFrame([{
                                "Company":     r["company_name"],
                                "Flag":        "🚨 YES" if r["manipulation_flag"] else "✅ NO",
                                "Risk Level":  r["risk_level"],
                                "Risk Score":  f"{r['risk_score']:.1f}",
                                "Probability": f"{r['manipulation_probability']*100:.1f}%",
                                "Top Alert":   r["alerts"][0] if r["alerts"] else "",
                            } for r in results])
                            st.dataframe(table_df, use_container_width=True, height=360)

                            st.download_button(
                                "⬇️ Download Results CSV",
                                pd.DataFrame([{
                                    "company": r["company_name"], "flag": r["manipulation_flag"],
                                    "risk_level": r["risk_level"], "risk_score": r["risk_score"],
                                    "probability": r["manipulation_probability"],
                                } for r in results]).to_csv(index=False).encode(),
                                file_name="finsentinel_results.csv", mime="text/csv"
                            )

                            st.markdown('<div class="section-title">🔍 Company Deep-Dive</div>', unsafe_allow_html=True)

                        else:
                            st.error(f"API Error {response.status_code}: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Drilldown — OUTSIDE button block, reads from session_state ──
    if st.session_state.batch_results:
        results = st.session_state.batch_results
        st.markdown('<div class="section-title">🔍 Company Deep-Dive</div>', unsafe_allow_html=True)
        company_names = [r["company_name"] for r in results]
        selected = st.selectbox(
            "Select a company to inspect:",
            company_names,
            key="drilldown_select"
        )
        # Find and show the selected company result
        selected_result = next((r for r in results if r["company_name"] == selected), None)
        if selected_result:
            show_result_panel(selected_result)


# ══════════════════════════════
# TAB 3 — Feature Importance
# ══════════════════════════════
with tab3:
    st.markdown('<div class="section-title">🌟 Global Feature Importance</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;font-size:0.85rem;margin-bottom:1rem;">Which financial ratios contribute most to predicting manipulation risk?</div>',
                unsafe_allow_html=True)

    if st.button("📊 Load Feature Importance", key="fi_btn"):
        if not api_alive:
            st.error("❌ Backend API not running.")
        else:
            with st.spinner("Loading model insights..."):
                try:
                    resp = requests.get(f"{API_URL}/feature-importance",
                                        params={"model_type": model_key}, timeout=30)
                    if resp.status_code == 200:
                        fi   = resp.json()
                        pairs = sorted(zip(fi["features"], fi["importances"]),
                                       key=lambda x: x[1], reverse=True)
                        f_s = [p[0].replace("_", " ").title() for p in pairs]
                        i_s = [p[1] for p in pairs]

                        fig, ax = plt.subplots(figsize=(8, 5))
                        fig.patch.set_facecolor("#ffffff")
                        ax.set_facecolor("#f8fafc")
                        gradient = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(f_s)))
                        bars = ax.barh(f_s[::-1], i_s[::-1], color=gradient,
                                       edgecolor="none", height=0.65)
                        for bar, val in zip(bars, i_s[::-1]):
                            ax.text(val + 0.003, bar.get_y() + bar.get_height() / 2,
                                    f"{val:.3f}", va="center", color="#1e293b", fontsize=9)
                        ax.set_xlabel("Importance Score", color="#475569", fontsize=10)
                        ax.set_title(f"Feature Importance — {fi['model_type'].replace('_',' ').title()}",
                                     color="#1e3a5f", fontsize=13, fontweight="bold", pad=15)
                        ax.tick_params(colors="#475569")
                        for spine in ax.spines.values():
                            spine.set_edgecolor("#e2e8f0")
                        plt.tight_layout()
                        st.pyplot(fig, use_container_width=True)
                        fi_df = pd.DataFrame({"Rank": range(1, len(f_s)+1),
                                              "Feature": f_s, "Importance": i_s})
                        st.dataframe(fi_df, use_container_width=True, hide_index=True)
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("""
    <div style='background:#ffffff;border-radius:12px;padding:1.5rem;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.05);'>
    <div style='color:#1e3a5f;font-weight:700;font-size:1rem;margin-bottom:1rem;'>📚 Signal Reference Guide</div>
    <table style='width:100%;color:#475569;font-size:0.85rem;border-collapse:collapse;'>
    <tr style='border-bottom:1px solid #e2e8f0;'>
        <th style='text-align:left;padding:8px;color:#1e3a5f;'>Signal</th>
        <th style='text-align:left;padding:8px;color:#1e3a5f;'>Formula</th>
        <th style='text-align:left;padding:8px;color:#1e3a5f;'>Red Flag</th>
    </tr>
    <tr style='border-bottom:1px solid #f1f5f9;'><td style='padding:8px;'>Accruals Ratio</td><td style='padding:8px;'>(Net Income − CFO) / Assets</td><td style='padding:8px;color:#ef4444;font-weight:600;'>&gt; 0.10</td></tr>
    <tr style='border-bottom:1px solid #f1f5f9;'><td style='padding:8px;'>Cash Flow / Income</td><td style='padding:8px;'>CFO / Net Income</td><td style='padding:8px;color:#ef4444;font-weight:600;'>&lt; 0.50</td></tr>
    <tr style='border-bottom:1px solid #f1f5f9;'><td style='padding:8px;'>Receivables / Revenue</td><td style='padding:8px;'>AR / Revenue</td><td style='padding:8px;color:#ef4444;font-weight:600;'>&gt; 0.30</td></tr>
    <tr style='border-bottom:1px solid #f1f5f9;'><td style='padding:8px;'>Debt-to-Equity</td><td style='padding:8px;'>Total Debt / Equity</td><td style='padding:8px;color:#ef4444;font-weight:600;'>&gt; 2.0</td></tr>
    <tr style='border-bottom:1px solid #f1f5f9;'><td style='padding:8px;'>Liabilities / Assets</td><td style='padding:8px;'>Total Liabilities / Assets</td><td style='padding:8px;color:#ef4444;font-weight:600;'>&gt; 0.80</td></tr>
    <tr><td style='padding:8px;'>ROA</td><td style='padding:8px;'>Net Income / Total Assets</td><td style='padding:8px;color:#ef4444;font-weight:600;'>&lt; 0</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)
