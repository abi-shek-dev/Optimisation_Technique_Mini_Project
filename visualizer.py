"""
visualizer.py
=============
Visualization module for the Queue Optimization System.

Generates matplotlib plots to visually explore how queue metrics
behave as arrival rate, utilization, and server count change.

Requires: matplotlib (install with: pip install matplotlib)
"""

import math

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from queue_model import MM1Queue, MMCQueue
from simulation import run_arrival_sweep


def _check_matplotlib() -> bool:
    """Checks if matplotlib is installed and warns the user if not."""
    if not MATPLOTLIB_AVAILABLE:
        print("\n  ⚠  matplotlib is not installed.")
        print("     Run:  pip install matplotlib")
        print("     Then restart the program to use visualization.\n")
        return False
    return True


# ─────────────────────────────────────────────
#  Plot 1: Waiting Time vs Arrival Rate
# ─────────────────────────────────────────────

def plot_wq_vs_lambda(mu: float = 15.0, server_counts: list = None) -> None:
    """
    Plots average waiting time (Wq) vs arrival rate (λ) for different
    numbers of servers side-by-side.

    This clearly shows how adding servers dramatically reduces wait times,
    especially as the system approaches its capacity.

    Parameters
    ----------
    mu            : float — Service rate per server
    server_counts : list  — List of server counts to compare (default: [1, 2, 3])
    """
    if not _check_matplotlib():
        return

    if server_counts is None:
        server_counts = [1, 2, 3]

    plt.figure(figsize=(10, 5))
    plt.style.use('seaborn-v0_8-darkgrid')

    colors = ['#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6']

    for i, c in enumerate(server_counts):
        # Sweep λ from 1 to 95% of capacity
        data = run_arrival_sweep(mu=mu, num_servers=c, steps=200)
        lam_vals = [d['lam'] for d in data]
        wq_vals  = [d['Wq'] * 60 for d in data]   # Convert to minutes

        label = f"M/M/{c}  (capacity = {c * mu}/hr)"
        plt.plot(lam_vals, wq_vals, label=label, color=colors[i % len(colors)],
                 linewidth=2.5)

    plt.title("Average Queue Wait Time (Wq) vs Arrival Rate (λ)", fontsize=14, fontweight='bold')
    plt.xlabel("Arrival Rate λ (customers/hour)", fontsize=12)
    plt.ylabel("Average Waiting Time Wq (minutes)", fontsize=12)
    plt.legend(fontsize=10)
    plt.ylim(0, None)
    plt.tight_layout()
    plt.savefig("plot_wq_vs_lambda.png", dpi=150)
    plt.show()
    print("  📊 Plot saved as 'plot_wq_vs_lambda.png'")


# ─────────────────────────────────────────────
#  Plot 2: Queue Metrics Dashboard
# ─────────────────────────────────────────────

def plot_metrics_dashboard(mu: float = 15.0, c: int = 1) -> None:
    """
    Plots a 2x2 dashboard showing all four key metrics vs arrival rate:
      - Utilization (ρ)
      - Avg customers in system (L)
      - Avg customers in queue (Lq)
      - Avg wait time in queue (Wq)

    Parameters
    ----------
    mu : float — Service rate per server
    c  : int   — Number of servers
    """
    if not _check_matplotlib():
        return

    data = run_arrival_sweep(mu=mu, num_servers=c, steps=200)
    if not data:
        print("  ⚠  No stable data points to plot.")
        return

    lam_vals = [d['lam']     for d in data]
    rho_vals = [d['rho']     for d in data]
    L_vals   = [d['L']       for d in data]
    Lq_vals  = [d['Lq']      for d in data]
    Wq_vals  = [d['Wq'] * 60 for d in data]   # minutes

    fig = plt.figure(figsize=(13, 9))
    fig.suptitle(f"M/M/{c} Queue — Full Metrics Dashboard  (μ = {mu}/hr)",
                 fontsize=15, fontweight='bold')

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    # ── Subplot 1: Utilization ──
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(lam_vals, rho_vals, color='#3498db', linewidth=2)
    ax1.axhline(y=0.8, color='orange', linestyle='--', linewidth=1.5, label='80% threshold')
    ax1.axhline(y=1.0, color='red',    linestyle='--', linewidth=1.5, label='Capacity limit')
    ax1.set_title("Utilization (ρ)", fontsize=12)
    ax1.set_xlabel("Arrival Rate λ")
    ax1.set_ylabel("ρ")
    ax1.legend(fontsize=8)
    ax1.set_ylim(0, 1.1)

    # ── Subplot 2: Avg customers in system ──
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(lam_vals, L_vals, color='#2ecc71', linewidth=2)
    ax2.set_title("Avg Customers in System (L)", fontsize=12)
    ax2.set_xlabel("Arrival Rate λ")
    ax2.set_ylabel("L")

    # ── Subplot 3: Avg customers in queue ──
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(lam_vals, Lq_vals, color='#e74c3c', linewidth=2)
    ax3.set_title("Avg Customers in Queue (Lq)", fontsize=12)
    ax3.set_xlabel("Arrival Rate λ")
    ax3.set_ylabel("Lq")

    # ── Subplot 4: Avg wait time ──
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(lam_vals, Wq_vals, color='#9b59b6', linewidth=2)
    ax4.set_title("Avg Queue Wait Time (Wq)", fontsize=12)
    ax4.set_xlabel("Arrival Rate λ")
    ax4.set_ylabel("Wq (minutes)")

    plt.savefig("plot_dashboard.png", dpi=150)
    plt.show()
    print("  📊 Dashboard saved as 'plot_dashboard.png'")


# ─────────────────────────────────────────────
#  Plot 3: Peak vs Non-Peak Bar Chart
# ─────────────────────────────────────────────

def plot_peak_vs_nonpeak(scenarios: list[dict], num_servers: int = 1) -> None:
    """
    Plots a bar chart comparing queue wait time (Wq) across time periods.
    Perfect for showing how peak hours are affected.

    Parameters
    ----------
    scenarios   : list of dict — Each has 'period', 'lam', 'mu'
    num_servers : int          — Number of servers
    """
    if not _check_matplotlib():
        return

    periods  = []
    wq_vals  = []
    colors   = []

    for s in scenarios:
        lam, mu = s['lam'], s['mu']

        if num_servers == 1:
            q = MM1Queue(lam, mu)
        else:
            q = MMCQueue(lam, mu, num_servers)

        periods.append(s['period'])

        if q.is_stable:
            wq_mins = q.Wq * 60   # convert to minutes
            wq_vals.append(wq_mins)
            # Color based on utilization
            if q.rho > 0.8:
                colors.append('#e74c3c')     # Red — high load
            elif q.rho > 0.5:
                colors.append('#f39c12')     # Orange — moderate
            else:
                colors.append('#2ecc71')     # Green — efficient
        else:
            wq_vals.append(0)
            colors.append('#c0392b')         # Dark red — unstable

    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.bar(range(len(periods)), wq_vals, color=colors, edgecolor='white',
                  linewidth=1.2, width=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, wq_vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{val:.1f} min",
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, rotation=20, ha='right', fontsize=9)
    ax.set_ylabel("Average Queue Waiting Time (minutes)", fontsize=11)
    ax.set_title(f"Peak vs Non-Peak Queue Wait Times  (c = {num_servers} server{'s' if num_servers > 1 else ''})",
                 fontsize=13, fontweight='bold')

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='Low Load (ρ ≤ 50%)'),
        Patch(facecolor='#f39c12', label='Moderate Load (50% < ρ ≤ 80%)'),
        Patch(facecolor='#e74c3c', label='High Load (ρ > 80%)'),
    ]
    ax.legend(handles=legend_elements, fontsize=9)

    plt.tight_layout()
    plt.savefig("plot_peak_nonpeak.png", dpi=150)
    plt.show()
    print("  📊 Bar chart saved as 'plot_peak_nonpeak.png'")
