"""
main.py
=======
Entry point for the Smart Campus Queue & Resource Optimization System.

This interactive menu-driven program lets you:
  1. Analyze a single M/M/1 queue
  2. Analyze a multi-server M/M/c queue
  3. Run time-period simulations (peak vs. non-peak)
  4. Compare server configurations
  5. Run sensitivity analysis (sweep arrival rates)
  6. Generate visualizations (requires matplotlib)

Usage:
    python main.py

Author  : [Your Name]
Subject : Operations Research / Optimisation Techniques
"""

from queue_model import MM1Queue, MMCQueue
from simulation import (
    run_time_period_simulation,
    run_arrival_sweep,
    print_sweep_table,
    compare_server_counts,
    SCENARIOS,
)
from utils import (
    print_header,
    print_results,
    get_float_input,
    get_int_input,
)
from visualizer import (
    plot_wq_vs_lambda,
    plot_metrics_dashboard,
    plot_peak_vs_nonpeak,
    MATPLOTLIB_AVAILABLE,
)


# ─────────────────────────────────────────────
#  Menu Handlers
# ─────────────────────────────────────────────

def menu_mm1_analysis() -> None:
    """
    Interactive M/M/1 queue analysis.
    Prompts the user for λ and μ, then displays all computed metrics.
    """
    print_header("M/M/1 Queue — Single Server Analysis")
    print("  Enter the queue parameters below.\n")

    lam = get_float_input("  Arrival rate λ (customers/unit time) : ")
    mu  = get_float_input("  Service rate μ (customers/unit time) : ")

    queue = MM1Queue(lam, mu)

    if not queue.is_stable:
        print("\n  ⚠️  WARNING: λ ≥ μ → Queue is UNSTABLE.")
        print("     In a real system, the queue would grow without bound.")
        print("     Metrics are meaningless in this state.\n")
    else:
        print_results(queue.results())


def menu_mmc_analysis() -> None:
    """
    Interactive M/M/c multi-server queue analysis.
    Prompts for λ, μ, and c, then displays all metrics.
    """
    print_header("M/M/c Queue — Multi-Server Analysis")
    print("  Enter the queue parameters below.\n")

    lam = get_float_input("  Arrival rate λ (customers/unit time) : ")
    mu  = get_float_input("  Service rate μ per server (customers/unit time) : ")
    c   = get_int_input(  "  Number of servers c                  : ")

    queue = MMCQueue(lam, mu, c)

    if not queue.is_stable:
        print(f"\n  ⚠️  WARNING: System is UNSTABLE (λ={lam} ≥ c·μ={c*mu}).")
        print("     Add more servers or reduce the arrival rate.\n")
    else:
        print_results(queue.results())


def menu_time_simulation() -> None:
    """
    Runs a time-period simulation for a chosen campus location.
    Shows how queue behavior changes throughout the day.
    """
    print_header("Time-Period Simulation")
    print("  Choose a campus location:\n")
    print("    1. College Canteen")
    print("    2. Library")
    print("    3. Service Counter (Admin/Fee)")

    choice = get_int_input("\n  Enter choice (1-3) : ", min_val=1)
    locations = {1: "canteen", 2: "library", 3: "service_counter"}
    location  = locations.get(choice, "canteen")

    c = get_int_input("\n  Number of servers to simulate : ")

    run_time_period_simulation(location=location, num_servers=c)

    # Offer to plot it
    if MATPLOTLIB_AVAILABLE:
        plot_it = input("\n  📊 Show bar chart for this simulation? (y/n) : ").strip().lower()
        if plot_it == 'y':
            mu_default = SCENARIOS[location][0]["mu"]
            plot_peak_vs_nonpeak(SCENARIOS[location], num_servers=c)


def menu_server_comparison() -> None:
    """
    Compares system performance for c = 1, 2, 3, … servers at fixed λ and μ.
    Helps decide how many servers are needed.
    """
    print_header("Server Count Comparison")
    print("  We'll compare performance for 1 to N servers at a fixed λ and μ.\n")

    lam       = get_float_input("  Arrival rate λ                : ")
    mu        = get_float_input("  Service rate μ per server     : ")
    max_c     = get_int_input(  "  Max servers to compare (N)   : ")

    compare_server_counts(lam=lam, mu=mu, max_servers=max_c)


def menu_sensitivity_analysis() -> None:
    """
    Sweeps arrival rate from a low value to near capacity and records
    how all queue metrics change. Useful for planning capacity.
    """
    print_header("Sensitivity Analysis — Arrival Rate Sweep")
    print("  We vary λ from a minimum to near system capacity.\n")

    mu    = get_float_input("  Service rate μ per server    : ")
    c     = get_int_input(  "  Number of servers (c)        : ")
    steps = get_int_input(  "  Number of data points (10+)  : ", min_val=2)

    data = run_arrival_sweep(mu=mu, num_servers=c, steps=steps)
    print_sweep_table(data)

    # Offer to plot
    if MATPLOTLIB_AVAILABLE:
        plot_it = input("\n  📊 Plot Wq vs λ for this setup? (y/n) : ").strip().lower()
        if plot_it == 'y':
            plot_wq_vs_lambda(mu=mu, server_counts=[c])


def menu_visualizations() -> None:
    """
    Visualization menu — generates matplotlib graphs.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("\n  ⚠  matplotlib is not installed. Run: pip install matplotlib\n")
        return

    print_header("Visualization Menu")
    print("  1. Wq vs λ  (compare multiple server counts)")
    print("  2. Full Metrics Dashboard (2×2 grid)")
    print("  3. Peak vs Non-Peak Bar Chart (canteen scenario)")

    choice = get_int_input("\n  Enter choice (1-3) : ", min_val=1)

    if choice == 1:
        mu = get_float_input("  Service rate μ per server : ")
        plot_wq_vs_lambda(mu=mu, server_counts=[1, 2, 3])

    elif choice == 2:
        mu = get_float_input("  Service rate μ per server : ")
        c  = get_int_input(  "  Number of servers (c)     : ")
        plot_metrics_dashboard(mu=mu, c=c)

    elif choice == 3:
        c = get_int_input("  Number of servers to simulate : ")
        plot_peak_vs_nonpeak(SCENARIOS["canteen"], num_servers=c)

    else:
        print("  ⚠  Invalid choice.")


# ─────────────────────────────────────────────
#  Main Menu Loop
# ─────────────────────────────────────────────

MENU_ITEMS = {
    "1": ("M/M/1  — Single Server Analysis",          menu_mm1_analysis),
    "2": ("M/M/c  — Multi-Server Analysis",           menu_mmc_analysis),
    "3": ("Time-Period Simulation (Peak / Off-Peak)",  menu_time_simulation),
    "4": ("Server Count Comparison",                  menu_server_comparison),
    "5": ("Sensitivity Analysis (Arrival Rate Sweep)", menu_sensitivity_analysis),
    "6": ("[Chart] Visualizations (requires matplotlib)",   menu_visualizations),
    "0": ("Exit",                                     None),
}


def print_main_menu() -> None:
    """Prints the main navigation menu."""
    print("\n")
    print("  +" + "=" * 54 + "+")
    print("  |   Smart Campus Queue & Resource Optimization System  |")
    print("  |         Operations Research Mini Project             |")
    print("  +" + "=" * 54 + "+")
    print()
    for key, (label, _) in MENU_ITEMS.items():
        print(f"    [{key}]  {label}")
    print()


def main() -> None:
    """
    Main program loop.
    Continuously shows the menu until the user chooses to exit.
    """
    while True:
        print_main_menu()
        choice = input("  Enter your choice : ").strip()

        if choice == "0":
            print("\n  Goodbye! Good luck with your viva!\n")
            break
        elif choice in MENU_ITEMS:
            _, handler = MENU_ITEMS[choice]
            try:
                handler()
            except KeyboardInterrupt:
                print("\n  (Returning to main menu...)")
            except Exception as e:
                print(f"\n  ⚠️  An error occurred: {e}")
        else:
            print("\n  ⚠  Invalid choice. Please enter a number from the menu.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
