"""
app.py
======
Streamlit Web Frontend for the Smart Campus Queue Optimization System.

Run with:
    streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math

from queue_model import MM1Queue, MMCQueue
from simulation import run_arrival_sweep, compare_server_counts, SCENARIOS
from utils import smart_suggestion

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Campus Queue Optimizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
}
[data-testid="stSidebar"] * { color: #e0e0ff !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 15px; }

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] label { color: #a0aec0 !important; font-size: 13px; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #63b3ed !important; font-size: 28px; font-weight: 700;
}

/* Page background */
.stApp { background: #0d1117; color: #c9d1d9; }

/* Section headers */
.section-header {
    background: linear-gradient(90deg, #0f3460, #533483);
    border-radius: 10px;
    padding: 12px 20px;
    margin: 20px 0 15px 0;
    font-size: 18px;
    font-weight: 600;
    color: white;
}

/* Suggestion boxes */
.suggest-red    { background:#2d1b1b; border-left:4px solid #fc8181; padding:12px 16px; border-radius:8px; margin:8px 0; color:#fed7d7; }
.suggest-orange { background:#2d2118; border-left:4px solid #f6ad55; padding:12px 16px; border-radius:8px; margin:8px 0; color:#feebc8; }
.suggest-yellow { background:#2d2a18; border-left:4px solid #f6e05e; padding:12px 16px; border-radius:8px; margin:8px 0; color:#fefcbf; }
.suggest-green  { background:#1a2d1b; border-left:4px solid #68d391; padding:12px 16px; border-radius:8px; margin:8px 0; color:#c6f6d5; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; }

/* Sliders */
[data-testid="stSlider"] > div { color: #63b3ed; }

/* Tabs */
[data-testid="stTabs"] button { color: #a0aec0; font-weight: 600; }
[data-testid="stTabs"] button[aria-selected="true"] { color: #63b3ed; border-bottom: 2px solid #63b3ed; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────

def suggestion_box(rho: float):
    """Renders a colored suggestion box based on utilization."""
    lines = smart_suggestion(rho)
    text  = "<br>".join(lines)
    if rho >= 1.0 or rho > 0.80:
        css = "suggest-red"
    elif rho > 0.50:
        css = "suggest-orange"
    else:
        css = "suggest-green"
    st.markdown(f'<div class="{css}">{text}</div>', unsafe_allow_html=True)


def rho_gauge_color(rho: float) -> str:
    if rho >= 0.8:  return "#fc8181"
    if rho >= 0.5:  return "#f6ad55"
    return "#68d391"


def make_wq_plot(mu: float, server_counts: list) -> plt.Figure:
    """Line chart: Wq vs Lambda for multiple server counts."""
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")
    colors = ["#fc8181", "#f6ad55", "#68d391", "#63b3ed", "#b794f4"]
    for i, c in enumerate(server_counts):
        data = run_arrival_sweep(mu=mu, num_servers=c, steps=200)
        if data:
            ax.plot([d["lam"] for d in data], [d["Wq"] * 60 for d in data],
                    color=colors[i % len(colors)], linewidth=2.5,
                    label=f"M/M/{c}  (cap={c*mu}/hr)")
    ax.set_title("Avg Queue Wait Time vs Arrival Rate", color="white", fontsize=13)
    ax.set_xlabel("Arrival Rate λ (customers/hr)", color="#a0aec0")
    ax.set_ylabel("Avg Wait Time Wq (minutes)", color="#a0aec0")
    ax.tick_params(colors="#a0aec0")
    ax.spines[:].set_color("#30363d")
    ax.legend(facecolor="#161b22", labelcolor="white", fontsize=9)
    ax.grid(alpha=0.15)
    fig.tight_layout()
    return fig


def make_dashboard_plot(mu: float, c: int) -> plt.Figure:
    """2x2 metrics dashboard."""
    data = run_arrival_sweep(mu=mu, num_servers=c, steps=200)
    if not data:
        return None
    lam = [d["lam"] for d in data]
    fig = plt.figure(figsize=(10, 7))
    fig.patch.set_facecolor("#0d1117")
    fig.suptitle(f"M/M/{c} Queue Dashboard  (mu={mu}/hr)", color="white", fontsize=14)
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    plots = [
        (0, 0, [d["rho"] for d in data], "Utilization (rho)", "#63b3ed"),
        (0, 1, [d["L"]   for d in data], "Avg in System (L)",  "#68d391"),
        (1, 0, [d["Lq"]  for d in data], "Avg in Queue (Lq)",  "#fc8181"),
        (1, 1, [d["Wq"] * 60 for d in data], "Avg Wait Wq (min)", "#b794f4"),
    ]
    for r, c_idx, y, title, color in plots:
        ax = fig.add_subplot(gs[r, c_idx])
        ax.set_facecolor("#161b22")
        ax.plot(lam, y, color=color, linewidth=2)
        ax.set_title(title, color="white", fontsize=11)
        ax.tick_params(colors="#a0aec0")
        ax.spines[:].set_color("#30363d")
        ax.grid(alpha=0.15)

    fig.tight_layout()
    return fig


def make_bar_chart(scenarios: list, num_servers: int) -> plt.Figure:
    """Peak vs non-peak bar chart."""
    periods, wq_vals, colors_list = [], [], []
    for s in scenarios:
        q = MM1Queue(s["lam"], s["mu"]) if num_servers == 1 else MMCQueue(s["lam"], s["mu"], num_servers)
        periods.append(s["period"])
        if q.is_stable:
            wq_vals.append(q.Wq * 60)
            colors_list.append("#fc8181" if q.rho > 0.8 else "#f6ad55" if q.rho > 0.5 else "#68d391")
        else:
            wq_vals.append(0)
            colors_list.append("#c53030")

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")
    bars = ax.bar(range(len(periods)), wq_vals, color=colors_list, edgecolor="#30363d", width=0.6)
    for bar, val in zip(bars, wq_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{val:.1f}", ha="center", va="bottom", color="white", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, rotation=20, ha="right", color="#a0aec0", fontsize=9)
    ax.set_ylabel("Avg Wait Time (minutes)", color="#a0aec0")
    ax.set_title(f"Peak vs Non-Peak Wait Times  (c={num_servers})", color="white", fontsize=13)
    ax.tick_params(colors="#a0aec0")
    ax.spines[:].set_color("#30363d")
    ax.grid(axis="y", alpha=0.15)
    fig.tight_layout()
    return fig


# ─── Sidebar Navigation ─────────────────────────────────────────────────────────

st.sidebar.markdown("## 🎓 Queue Optimizer")
st.sidebar.markdown("*Smart Campus Resource System*")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠  Home",
    "📊  M/M/1 Analysis",
    "🖥️  M/M/c Analysis",
    "🕐  Time Simulation",
    "🔢  Server Comparison",
    "📈  Visualizations",
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Subject:** Operations Research")
st.sidebar.markdown("**Models:** M/M/1 · M/M/c · Erlang C")


# ═══════════════════════════════════════════════════════
#  PAGE: HOME
# ═══════════════════════════════════════════════════════

if page == "🏠  Home":
    st.markdown("# 🎓 Smart Campus Queue & Resource Optimization System")
    st.markdown("##### Operations Research Mini Project — Queueing Theory")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📌 What is this?")
        st.write("This system simulates and analyzes **waiting lines** at campus locations like canteens, libraries, and service counters using **Queueing Theory** formulas.")
    with col2:
        st.markdown("### 🧮 Models Used")
        st.write("**M/M/1** — Single server queue\n\n**M/M/c** — Multi-server queue\n\n**Erlang C** — Probability of waiting")
    with col3:
        st.markdown("### 🎯 Goal")
        st.write("Find the **optimal number of servers** to minimize customer wait time while keeping operating costs low.")

    st.markdown("---")
    st.markdown('<div class="section-header">📐 Key Formulas (M/M/1)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.latex(r"\rho = \frac{\lambda}{\mu}")
        st.caption("Utilization — fraction of time server is busy")
        st.latex(r"L = \frac{\rho}{1 - \rho}")
        st.caption("Avg customers in system")
        st.latex(r"W = \frac{1}{\mu - \lambda}")
        st.caption("Avg time in system (Little's Law)")
    with col2:
        st.latex(r"L_q = \frac{\rho^2}{1 - \rho}")
        st.caption("Avg customers waiting in queue")
        st.latex(r"W_q = \frac{\lambda}{\mu(\mu - \lambda)}")
        st.caption("Avg waiting time in queue")
        st.latex(r"P_0 = 1 - \rho")
        st.caption("Probability server is idle")

    st.markdown("---")
    st.info("**Little's Law:**  L = λ · W   and   Lq = λ · Wq  — connects all metrics universally.")
    st.warning("**Stability Condition:** λ must be less than μ (M/M/1) or c·μ (M/M/c), otherwise the queue grows infinitely.")


# ═══════════════════════════════════════════════════════
#  PAGE: M/M/1 ANALYSIS
# ═══════════════════════════════════════════════════════

elif page == "📊  M/M/1 Analysis":
    st.markdown("# 📊 M/M/1 Queue — Single Server Analysis")
    st.markdown("Model a single-server queue (one canteen counter, one librarian, etc.)")
    st.markdown("---")

    col_in, col_out = st.columns([1, 2])

    with col_in:
        st.markdown("### ⚙️ Parameters")
        lam = st.slider("Arrival Rate λ (customers/hr)", 1.0, 100.0, 10.0, 0.5)
        mu  = st.slider("Service Rate μ (customers/hr)", 1.0, 100.0, 15.0, 0.5)
        st.markdown(f"**System capacity:** {mu:.1f} customers/hr")

    with col_out:
        q = MM1Queue(lam, mu)
        st.markdown("### 📋 Results")

        if not q.is_stable:
            st.error(f"⚠️ UNSTABLE SYSTEM — λ ({lam}) ≥ μ ({mu}). Queue grows infinitely! Add more servers or reduce arrivals.")
        else:
            rho_color = rho_gauge_color(q.rho)
            c1, c2, c3 = st.columns(3)
            c1.metric("Utilization ρ",       f"{q.rho:.3f}",  f"{q.rho*100:.1f}%")
            c2.metric("Avg in System (L)",   f"{q.L:.3f}",    "customers")
            c3.metric("Avg in Queue (Lq)",   f"{q.Lq:.3f}",   "customers")

            c4, c5, c6 = st.columns(3)
            c4.metric("Time in System (W)",  f"{q.W:.4f}",    "hours")
            c5.metric("Wait in Queue (Wq)",  f"{q.Wq*60:.2f}","minutes")
            c6.metric("Server Idle (P0)",    f"{q.P0:.3f}",   f"{q.P0*100:.1f}%")

            st.markdown("### 💡 Smart Suggestion")
            suggestion_box(q.rho)

            st.markdown("### 📊 Utilization Gauge")
            st.progress(min(q.rho, 1.0))
            st.caption(f"Server is busy {q.rho*100:.1f}% of the time")


# ═══════════════════════════════════════════════════════
#  PAGE: M/M/c ANALYSIS
# ═══════════════════════════════════════════════════════

elif page == "🖥️  M/M/c Analysis":
    st.markdown("# 🖥️ M/M/c Queue — Multi-Server Analysis")
    st.markdown("Model multiple parallel servers with one shared queue (e.g., 3 canteen counters).")
    st.markdown("---")

    col_in, col_out = st.columns([1, 2])

    with col_in:
        st.markdown("### ⚙️ Parameters")
        lam = st.slider("Arrival Rate λ (customers/hr)", 1.0, 150.0, 25.0, 0.5)
        mu  = st.slider("Service Rate μ per server",     1.0, 50.0,  15.0, 0.5)
        c   = st.slider("Number of Servers (c)",         1, 10, 2)
        st.markdown(f"**Total capacity:** {c * mu:.1f} customers/hr")

    with col_out:
        q = MMCQueue(lam, mu, c)
        st.markdown("### 📋 Results")

        if not q.is_stable:
            st.error(f"⚠️ UNSTABLE — λ ({lam}) ≥ c·μ ({c*mu}). Need at least {math.ceil(lam/mu)} servers!")
            min_c = math.ceil(lam / mu) + 1
            st.info(f"💡 Try setting servers to **{min_c}** to stabilize the system.")
        else:
            ec = q._erlang_c()
            c1, c2, c3 = st.columns(3)
            c1.metric("Utilization ρ",       f"{q.rho:.3f}",  f"{q.rho*100:.1f}%")
            c2.metric("Erlang C",            f"{ec:.3f}",     f"{ec*100:.1f}% chance of waiting")
            c3.metric("Avg in System (L)",   f"{q.L:.3f}",    "customers")

            c4, c5, c6 = st.columns(3)
            c4.metric("Avg in Queue (Lq)",   f"{q.Lq:.3f}",   "customers")
            c5.metric("Time in System (W)",  f"{q.W:.4f}",    "hours")
            c6.metric("Wait in Queue (Wq)",  f"{q.Wq*60:.2f}","minutes")

            st.markdown("### 💡 Smart Suggestion")
            suggestion_box(q.rho)

            st.markdown("### 📊 Per-Server Utilization")
            st.progress(min(q.rho, 1.0))
            st.caption(f"Each server is busy {q.rho*100:.1f}% of the time")


# ═══════════════════════════════════════════════════════
#  PAGE: TIME SIMULATION
# ═══════════════════════════════════════════════════════

elif page == "🕐  Time Simulation":
    st.markdown("# 🕐 Time-Period Simulation — Peak vs Off-Peak")
    st.markdown("See how queue metrics change across different times of day.")
    st.markdown("---")

    loc_map = {"College Canteen": "canteen", "Library": "library", "Service Counter": "service_counter"}
    location_label = st.selectbox("Select Campus Location", list(loc_map.keys()))
    location = loc_map[location_label]
    num_servers = st.slider("Number of Servers", 1, 8, 1)

    st.markdown("---")

    scenarios = SCENARIOS[location]
    rows = []
    for s in scenarios:
        q = MM1Queue(s["lam"], s["mu"]) if num_servers == 1 else MMCQueue(s["lam"], s["mu"], num_servers)
        if q.is_stable:
            rows.append({
                "Time Period":    s["period"],
                "λ (arr/hr)":    s["lam"],
                "μ (svc/hr)":    s["mu"],
                "Utilization ρ": f"{q.rho:.3f}",
                "L (system)":    f"{q.L:.2f}",
                "Wq (minutes)":  f"{q.Wq*60:.2f}",
                "Status":        "HIGH LOAD" if q.rho > 0.8 else "MODERATE" if q.rho > 0.5 else "EFFICIENT",
            })
        else:
            rows.append({
                "Time Period":    s["period"],
                "λ (arr/hr)":    s["lam"],
                "μ (svc/hr)":    s["mu"],
                "Utilization ρ": "inf",
                "L (system)":    "inf",
                "Wq (minutes)":  "inf",
                "Status":        "UNSTABLE",
            })

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### 📊 Wait Time Bar Chart")
    fig = make_bar_chart(scenarios, num_servers)
    st.pyplot(fig)
    plt.close(fig)


# ═══════════════════════════════════════════════════════
#  PAGE: SERVER COMPARISON
# ═══════════════════════════════════════════════════════

elif page == "🔢  Server Comparison":
    st.markdown("# 🔢 Server Count Comparison")
    st.markdown("Find the minimum number of servers needed to keep your queue stable and wait times acceptable.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1: lam = st.number_input("Arrival Rate λ (customers/hr)", 1.0, 200.0, 40.0, 1.0)
    with col2: mu  = st.number_input("Service Rate μ per server",      1.0, 100.0, 15.0, 1.0)
    with col3: max_c = st.slider("Max Servers to Test", 2, 10, 6)

    st.markdown("---")

    rows = []
    for c in range(1, max_c + 1):
        q = MMCQueue(lam, mu, c)
        stable = "Yes" if q.is_stable else "No"
        if q.is_stable:
            rows.append({"Servers (c)": c, "Stable": stable, "rho per server": f"{q.rho:.4f}",
                         "L (system)": f"{q.L:.3f}", "Lq (queue)": f"{q.Lq:.3f}",
                         "Wq (minutes)": f"{q.Wq*60:.3f}"})
        else:
            rows.append({"Servers (c)": c, "Stable": stable, "rho per server": f"{q.rho:.4f}",
                         "L (system)": "inf", "Lq (queue)": "inf", "Wq (minutes)": "inf"})

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    min_stable = math.ceil(lam / mu) + 1
    st.success(f"✅ Minimum servers needed for stability: **{min_stable}**")
    st.info("Tip: Pick the server count where Wq drops to an acceptable level — balance cost vs. wait time.")

    # Plot Wq vs server count
    stable_rows = [r for r in rows if r["Stable"] == "Yes"]
    if stable_rows:
        import pandas as pd
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        fig2.patch.set_facecolor("#0d1117")
        ax2.set_facecolor("#161b22")
        xs = [r["Servers (c)"] for r in stable_rows]
        ys = [float(r["Wq (minutes)"]) for r in stable_rows]
        ax2.plot(xs, ys, color="#63b3ed", linewidth=2.5, marker="o", markersize=7)
        ax2.set_xlabel("Number of Servers (c)", color="#a0aec0")
        ax2.set_ylabel("Avg Wait Time Wq (minutes)", color="#a0aec0")
        ax2.set_title("Wait Time vs Number of Servers", color="white")
        ax2.tick_params(colors="#a0aec0")
        ax2.spines[:].set_color("#30363d")
        ax2.grid(alpha=0.15)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)


# ═══════════════════════════════════════════════════════
#  PAGE: VISUALIZATIONS
# ═══════════════════════════════════════════════════════

elif page == "📈  Visualizations":
    st.markdown("# 📈 Visualizations")
    st.markdown("Explore queue behavior through interactive charts.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Wq vs Arrival Rate", "Full Dashboard", "Peak vs Non-Peak"])

    with tab1:
        st.markdown("### Wait Time vs Arrival Rate (Multiple Servers)")
        mu_v = st.slider("Service Rate μ", 5.0, 50.0, 15.0, 1.0, key="wq_mu")
        servers_sel = st.multiselect("Compare Servers", [1, 2, 3, 4, 5], default=[1, 2, 3])
        if servers_sel:
            fig = make_wq_plot(mu_v, servers_sel)
            st.pyplot(fig)
            plt.close(fig)
            st.caption("Notice how adding servers dramatically reduces wait time, especially near capacity.")

    with tab2:
        st.markdown("### Full Metrics Dashboard (2×2)")
        col1, col2 = st.columns(2)
        with col1: mu_d = st.slider("Service Rate μ", 5.0, 50.0, 15.0, 1.0, key="dash_mu")
        with col2: c_d  = st.slider("Servers (c)",    1, 8, 2,               key="dash_c")
        fig = make_dashboard_plot(mu_d, c_d)
        if fig:
            st.pyplot(fig)
            plt.close(fig)

    with tab3:
        st.markdown("### Peak vs Non-Peak Bar Chart")
        loc_map2 = {"College Canteen": "canteen", "Library": "library", "Service Counter": "service_counter"}
        loc2 = st.selectbox("Location", list(loc_map2.keys()), key="bar_loc")
        c_bar = st.slider("Servers", 1, 8, 1, key="bar_c")
        fig = make_bar_chart(SCENARIOS[loc_map2[loc2]], c_bar)
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Green = Efficient | Orange = Moderate Load | Red = High Load / Unstable")
