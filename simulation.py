"""
simulation.py
=============
Simulation module for the Queue Optimization System.

Simulates queue behavior across different time periods (peak vs. non-peak)
and across a range of arrival rates to study system performance trends.

Uses deterministic queueing formulas (not discrete-event simulation)
for clarity and simplicity — perfect for a college mini project.
"""

from queue_model import MM1Queue, MMCQueue
from utils import print_header, smart_suggestion


# ─────────────────────────────────────────────
#  Time-Period Simulation
# ─────────────────────────────────────────────

# Predefined scenarios for a typical college canteen/library
# Each scenario has: name, arrival rate (λ), service rate (μ), servers (c)
SCENARIOS = {
    "canteen": [
        {"period": "Early Morning (7-9 AM)",   "lam": 5,  "mu": 10, "note": "Before college starts"},
        {"period": "Morning Break (10-11 AM)", "lam": 20, "mu": 12, "note": "First break rush"},
        {"period": "Lunch Hour (1-2 PM)",      "lam": 45, "mu": 15, "note": "Peak lunch crowd"},
        {"period": "Afternoon (3-4 PM)",       "lam": 15, "mu": 15, "note": "Light snack time"},
        {"period": "Evening (5-6 PM)",         "lam": 8,  "mu": 10, "note": "End-of-day"},
    ],
    "library": [
        {"period": "Morning (9-11 AM)",        "lam": 4,  "mu": 8,  "note": "Study session start"},
        {"period": "Afternoon (1-3 PM)",       "lam": 12, "mu": 8,  "note": "Post-lunch rush"},
        {"period": "Exam Week - Afternoon",    "lam": 25, "mu": 8,  "note": "Peak exam period"},
        {"period": "Evening (6-8 PM)",         "lam": 6,  "mu": 8,  "note": "Evening readers"},
    ],
    "service_counter": [
        {"period": "Morning (9-10 AM)",        "lam": 10, "mu": 15, "note": "Fee/admin queries"},
        {"period": "Mid-Morning (11 AM-1 PM)", "lam": 28, "mu": 15, "note": "Form submission rush"},
        {"period": "Afternoon (2-4 PM)",       "lam": 18, "mu": 15, "note": "Moderate load"},
        {"period": "End of Day (4-5 PM)",      "lam": 8,  "mu": 15, "note": "Wind-down"},
    ],
}


def run_time_period_simulation(location: str = "canteen", num_servers: int = 1) -> None:
    """
    Simulates queue performance across multiple time periods for a given location.

    For each time period:
      - Computes M/M/1 metrics (if num_servers == 1)
      - Or M/M/c metrics (if num_servers > 1)
      - Prints metrics and suggestions

    Parameters
    ----------
    location    : str — One of 'canteen', 'library', 'service_counter'
    num_servers : int — Number of servers (c)
    """
    if location not in SCENARIOS:
        print(f"  ⚠  Unknown location '{location}'. Choose from: {list(SCENARIOS.keys())}")
        return

    scenarios = SCENARIOS[location]
    model_name = f"M/M/{num_servers}" if num_servers > 1 else "M/M/1"

    print_header(f"Time-Period Simulation -- {location.replace('_', ' ').title()} ({model_name})")
    print(f"  {'Period':<30} {'lam':>5} {'mu':>5} {'rho':>8} {'L':>8} {'Wq (min)':>10} {'Status'}")
    print(f"  {'-'*30} {'-'*5} {'-'*5} {'-'*8} {'-'*8} {'-'*10} {'-'*18}")

    for s in scenarios:
        lam, mu = s["lam"], s["mu"]

        # Choose model based on number of servers
        if num_servers == 1:
            q = MM1Queue(lam, mu)
        else:
            q = MMCQueue(lam, mu, num_servers)

        if q.is_stable:
            rho   = q.rho
            L     = q.L
            Wq    = q.Wq * 60     # Convert to minutes (assuming lam, mu are per hour)
            suggestions = smart_suggestion(rho)
            status = suggestions[0].split(":")[0].replace("[","").replace("]","")
        else:
            rho, L, Wq = float('inf'), float('inf'), float('inf')
            status = "UNSTABLE"

        # Format infinity nicely
        rho_str = f"{rho:.3f}" if rho != float('inf') else "  inf"
        L_str   = f"{L:.2f}"   if L   != float('inf') else "  inf"
        Wq_str  = f"{Wq:.2f}"  if Wq  != float('inf') else "  inf"

        print(f"  {s['period']:<30} {lam:>5} {mu:>5} {rho_str:>8} {L_str:>8} {Wq_str:>10}  {status}")

    print(f"\n  Note: lam = arrivals/hr, mu = service/hr, Wq is in minutes")
    print(f"  Tip : Add more servers for UNSTABLE and HIGH LOAD periods!")


# ---------------------------------------------
#  Arrival Rate Sweep (Sensitivity Analysis)
# ---------------------------------------------

def run_arrival_sweep(mu: float, num_servers: int = 1,
                      lam_start: float = 1.0, lam_end: float = None,
                      steps: int = 10) -> list[dict]:
    """
    Sweeps arrival rate (λ) from lam_start to near the system capacity
    and records queue metrics at each step.

    Useful for understanding how performance degrades as load increases.

    Parameters
    ----------
    mu          : float — Service rate per server
    num_servers : int   — Number of servers
    lam_start   : float — Starting arrival rate
    lam_end     : float — Ending arrival rate (default: 95% of capacity)
    steps       : int   — Number of data points

    Returns
    -------
    list of dict — Each dict has λ, ρ, L, Lq, W, Wq
    """
    capacity = num_servers * mu                         # Maximum throughput
    if lam_end is None:
        lam_end = 0.95 * capacity                       # Stay just below instability

    # Generate evenly spaced arrival rates
    step_size = (lam_end - lam_start) / (steps - 1)
    lam_values = [lam_start + i * step_size for i in range(steps)]

    data = []
    for lam in lam_values:
        if num_servers == 1:
            q = MM1Queue(lam, mu)
        else:
            q = MMCQueue(lam, mu, num_servers)

        if q.is_stable:
            data.append({
                "lam": round(lam, 3),
                "rho": round(q.rho, 4),
                "L":   round(q.L,   4),
                "Lq":  round(q.Lq,  4),
                "W":   round(q.W,   4),
                "Wq":  round(q.Wq,  4),
            })

    return data


def print_sweep_table(data: list[dict]) -> None:
    """
    Prints the arrival rate sweep data as a formatted table.

    Parameters
    ----------
    data : list of dict — Output from run_arrival_sweep()
    """
    print_header("Arrival Rate Sensitivity Analysis")
    print(f"  {'lam':>8} {'rho (util)':>10} {'L (sys)':>10} {'Lq (queue)':>12} {'W (sys)':>10} {'Wq (wait)':>10}")
    print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*12} {'-'*10} {'-'*10}")

    for row in data:
        print(f"  {row['lam']:>8.3f} {row['rho']:>10.4f} {row['L']:>10.4f} "
              f"{row['Lq']:>12.4f} {row['W']:>10.4f} {row['Wq']:>10.4f}")

    print(f"\n  Tip: Notice how Lq and Wq spike sharply as rho approaches 1.0 !")


# ─────────────────────────────────────────────
#  Server Comparison
# ─────────────────────────────────────────────

def compare_server_counts(lam: float, mu: float, max_servers: int = 5) -> None:
    """
    Compares performance as the number of servers increases from 1 to max_servers.

    Helps answer: "How many servers do I need to keep wait times acceptable?"

    Parameters
    ----------
    lam         : float — Arrival rate
    mu          : float — Service rate per server
    max_servers : int   — Maximum number of servers to evaluate
    """
    print_header(f"Server Count Comparison  (lam={lam}, mu={mu})")
    print(f"  {'Servers':>8} {'rho':>10} {'Stable':>8} {'L':>10} {'Lq':>10} {'Wq (min)':>12}")
    print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*10} {'-'*12}")

    for c in range(1, max_servers + 1):
        q = MMCQueue(lam, mu, c)
        stable = "Yes" if q.is_stable else "No"

        if q.is_stable:
            rho_str = f"{q.rho:.4f}"
            L_str   = f"{q.L:.4f}"
            Lq_str  = f"{q.Lq:.4f}"
            Wq_str  = f"{q.Wq * 60:.4f}"   # Convert to minutes
        else:
            rho_str = f"{q.rho:.4f}"
            L_str = Lq_str = Wq_str = "    inf"

        print(f"  {c:>8} {rho_str:>10} {stable:>8} {L_str:>10} {Lq_str:>10} {Wq_str:>12}")

    print(f"\n  Tip: Pick the minimum c that gives acceptable Wq!")
