"""
utils.py
========
Utility functions for the Queue Optimization System.

Contains:
  - print_results()       : Pretty-prints queue metrics
  - smart_suggestion()    : Gives operational advice based on utilization
  - get_float_input()     : Safe float input with validation
  - get_int_input()       : Safe integer input with validation
  - print_header()        : Prints section headers for better readability
"""

# ─────────────────────────────────────────────────────────
#  Console Display Helpers
# ─────────────────────────────────────────────────────────

def print_header(title: str) -> None:
    """
    Prints a formatted section header to the console.

    Example:
        ==================================================
          M/M/1 Queue Results
        ==================================================
    """
    width = 50
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_results(results: dict) -> None:
    """
    Displays queue model results in a clean, readable format.

    Parameters
    ----------
    results : dict
        Dictionary returned by MM1Queue.results() or MMCQueue.results()
    """
    print_header(f"{results['model']} Queue -- Performance Metrics")

    # -- Input Parameters --
    print(f"  {'Arrival Rate (lambda)':<35} {results['arrival_rate']:.4f} customers/unit time")
    print(f"  {'Service Rate (mu)':<35} {results['service_rate']:.4f} customers/unit time")

    if results['model'] == "M/M/c":
        print(f"  {'Number of Servers (c)':<35} {results['num_servers']}")
        print(f"  {'Erlang C -- P(waiting)':<35} {results['erlang_c']:.4f}  ({results['erlang_c']*100:.1f}%)")

    print()

    # -- System Status --
    if not results['is_stable']:
        print("  [!] SYSTEM IS UNSTABLE: lambda >= c*mu")
        print("      The queue will grow infinitely. Add more servers or reduce arrivals.")
        return

    rho_pct = results['utilization'] * 100
    print(f"  {'Utilization (rho)':<35} {results['utilization']:.4f}  ({rho_pct:.1f}%)")

    # -- Queue Metrics --
    print()
    print(f"  {'Avg customers in SYSTEM (L)':<35} {results['L_system']:.4f}")
    print(f"  {'Avg customers in QUEUE (Lq)':<35} {results['L_queue']:.4f}")
    print(f"  {'Avg time in SYSTEM (W)':<35} {results['W_system']:.4f} units")
    print(f"  {'Avg time in QUEUE (Wq)':<35} {results['W_queue']:.4f} units")

    if results['model'] == "M/M/1":
        print(f"  {'Prob. server is IDLE (P0)':<35} {results['P_idle']:.4f}  ({results['P_idle']*100:.1f}%)")

    print()

    # -- Smart Suggestion --
    print("  [*] Smart Suggestion:")
    suggestion = smart_suggestion(results['utilization'])
    for line in suggestion:
        print(f"     {line}")


# ─────────────────────────────────────────────────────────
#  Smart Suggestion Engine
# ─────────────────────────────────────────────────────────

def smart_suggestion(rho: float) -> list:
    """
    Provides operational recommendations based on server utilization.

    Rules:
      - rho >= 1.0  : System is overloaded (unstable)
      - rho > 0.80  : High load, risk of long queues
      - rho > 0.50  : Moderate load, acceptable performance
      - rho <= 0.50 : Low load, system is efficient

    Parameters
    ----------
    rho : float
        Utilization factor (lambda/mu for M/M/1, or lambda/(c*mu) for M/M/c)

    Returns
    -------
    list of str
        A list of suggestion lines to display.
    """
    if rho >= 1.0:
        return [
            "[CRITICAL] System is OVERLOADED.",
            "   -> Immediately add more servers.",
            "   -> Consider appointment/token systems to control arrival rate.",
        ]
    elif rho > 0.80:
        return [
            "[HIGH LOAD] Utilization is above 80%.",
            "   -> Consider adding 1-2 more servers during peak hours.",
            "   -> Implement express lanes or priority queues.",
            f"   -> Current utilization: {rho*100:.1f}%",
        ]
    elif rho > 0.50:
        return [
            "[MODERATE] System is under acceptable load.",
            "   -> Monitor during peak hours -- may need scaling.",
            f"   -> Current utilization: {rho*100:.1f}%",
        ]
    else:
        return [
            "[EFFICIENT] System is lightly loaded.",
            "   -> Resources may be over-provisioned; consider reducing servers during off-peak.",
            f"   -> Current utilization: {rho*100:.1f}%",
        ]


# ─────────────────────────────────────────────────────────
#  Safe Input Helpers
# ─────────────────────────────────────────────────────────

def get_float_input(prompt: str, min_val: float = 0.0) -> float:
    """
    Safely reads a positive float from the user.
    Repeats until a valid number greater than min_val is entered.

    Parameters
    ----------
    prompt  : str   -- The message shown to the user
    min_val : float -- The minimum acceptable value (exclusive)

    Returns
    -------
    float -- A valid float value
    """
    while True:
        try:
            value = float(input(prompt))
            if value <= min_val:
                print(f"  [!] Please enter a value greater than {min_val}.")
            else:
                return value
        except ValueError:
            print("  [!] Invalid input. Please enter a numeric value.")


def get_int_input(prompt: str, min_val: int = 1) -> int:
    """
    Safely reads a positive integer from the user.

    Parameters
    ----------
    prompt  : str -- The message shown to the user
    min_val : int -- The minimum acceptable value (inclusive)

    Returns
    -------
    int -- A valid integer
    """
    while True:
        try:
            value = int(input(prompt))
            if value < min_val:
                print(f"  [!] Please enter a value >= {min_val}.")
            else:
                return value
        except ValueError:
            print("  [!] Invalid input. Please enter a whole number.")
