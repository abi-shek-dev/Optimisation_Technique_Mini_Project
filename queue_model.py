"""
queue_model.py
==============
Core module for Queueing Theory Models.

Contains:
  - MM1Queue  : Single-server Markovian queue (M/M/1)
  - MMCQueue  : Multi-server Markovian queue (M/M/c)

Formulas are from Hillier & Lieberman, "Introduction to Operations Research"
"""

import math


# ─────────────────────────────────────────────
#  M/M/1 Queue Model
# ─────────────────────────────────────────────

class MM1Queue:
    """
    Represents an M/M/1 Queueing System.

    Assumptions:
      - Arrivals follow a Poisson process with rate λ (lambda)
      - Service times are exponentially distributed with rate μ (mu)
      - Single server, infinite queue capacity, FCFS discipline

    Parameters
    ----------
    lam : float
        Arrival rate (λ) — average number of customers arriving per unit time.
    mu  : float
        Service rate (μ) — average number of customers served per unit time.
    """

    def __init__(self, lam: float, mu: float):
        if lam <= 0 or mu <= 0:
            raise ValueError("Arrival rate (λ) and Service rate (μ) must be positive.")
        self.lam = lam
        self.mu = mu

    @property
    def is_stable(self) -> bool:
        """
        A queue is stable only when λ < μ.
        If λ >= μ, the queue grows infinitely — the system is overloaded.
        """
        return self.lam < self.mu

    @property
    def rho(self) -> float:
        """
        Utilization factor (ρ = λ / μ).
        Represents the fraction of time the server is busy.
        Must be < 1 for a stable queue.
        """
        return self.lam / self.mu

    @property
    def L(self) -> float:
        """
        Average number of customers IN THE SYSTEM (queue + being served).
        Formula: L = ρ / (1 - ρ)
        """
        if not self.is_stable:
            return float('inf')
        return self.rho / (1 - self.rho)

    @property
    def Lq(self) -> float:
        """
        Average number of customers WAITING IN THE QUEUE (not being served).
        Formula: Lq = ρ² / (1 - ρ)
        """
        if not self.is_stable:
            return float('inf')
        return (self.rho ** 2) / (1 - self.rho)

    @property
    def W(self) -> float:
        """
        Average time a customer spends IN THE SYSTEM (waiting + service).
        Formula: W = 1 / (μ - λ)
        Derived from Little's Law: W = L / λ
        """
        if not self.is_stable:
            return float('inf')
        return 1 / (self.mu - self.lam)

    @property
    def Wq(self) -> float:
        """
        Average time a customer spends WAITING IN THE QUEUE (before service begins).
        Formula: Wq = λ / (μ * (μ - λ))
        """
        if not self.is_stable:
            return float('inf')
        return self.lam / (self.mu * (self.mu - self.lam))

    @property
    def P0(self) -> float:
        """
        Probability that the system is EMPTY (server is idle).
        Formula: P0 = 1 - ρ
        """
        if not self.is_stable:
            return 0.0
        return 1 - self.rho

    def results(self) -> dict:
        """
        Returns all computed metrics as a dictionary.
        """
        return {
            "model":             "M/M/1",
            "arrival_rate":      self.lam,
            "service_rate":      self.mu,
            "utilization":       self.rho,
            "is_stable":         self.is_stable,
            "L_system":          self.L,
            "L_queue":           self.Lq,
            "W_system":          self.W,
            "W_queue":           self.Wq,
            "P_idle":            self.P0,
        }


# ─────────────────────────────────────────────
#  M/M/c Queue Model (Multi-Server)
# ─────────────────────────────────────────────

class MMCQueue:
    """
    Represents an M/M/c Queueing System (c servers, all with same rate μ).

    Assumptions:
      - Poisson arrivals at rate λ
      - Exponential service times with rate μ per server
      - c parallel servers, infinite queue, FCFS discipline

    Parameters
    ----------
    lam : float
        Arrival rate (λ)
    mu  : float
        Service rate per server (μ)
    c   : int
        Number of servers
    """

    def __init__(self, lam: float, mu: float, c: int):
        if lam <= 0 or mu <= 0:
            raise ValueError("λ and μ must be positive.")
        if c < 1:
            raise ValueError("Number of servers (c) must be at least 1.")
        self.lam = lam
        self.mu = mu
        self.c = c

    @property
    def is_stable(self) -> bool:
        """
        Stability condition for M/M/c: λ < c * μ
        Total service capacity must exceed the arrival rate.
        """
        return self.lam < self.c * self.mu

    @property
    def rho(self) -> float:
        """
        Server utilization per server.
        Formula: ρ = λ / (c * μ)
        """
        return self.lam / (self.c * self.mu)

    def _erlang_c(self) -> float:
        """
        Computes the Erlang C formula — C(c, λ/μ).

        This gives the probability that an arriving customer
        must WAIT (all servers are busy).

        Formula:
            Let a = λ/μ  (offered traffic load)

            Numerator   = (a^c / c!) * (1 / (1 - ρ))

            Denominator = Σ(k=0 to c-1) [a^k / k!]  +  Numerator

            C(c, a) = Numerator / Denominator
        """
        a = self.lam / self.mu          # offered load
        rho = self.rho                  # utilization per server

        if not self.is_stable:
            return 1.0                  # system overloaded → always waiting

        # Compute the sum for k = 0 to c-1
        sum_terms = sum((a ** k) / math.factorial(k) for k in range(self.c))

        # The final term (k = c), adjusted for steady state
        last_term = (a ** self.c) / (math.factorial(self.c) * (1 - rho))

        # Erlang C probability
        C = last_term / (sum_terms + last_term)
        return C

    @property
    def Lq(self) -> float:
        """
        Average number of customers waiting IN THE QUEUE.
        Formula: Lq = C(c, λ/μ) * ρ / (1 - ρ)
        """
        if not self.is_stable:
            return float('inf')
        return self._erlang_c() * self.rho / (1 - self.rho)

    @property
    def Wq(self) -> float:
        """
        Average waiting time IN THE QUEUE.
        Using Little's Law: Wq = Lq / λ
        """
        if not self.is_stable:
            return float('inf')
        return self.Lq / self.lam

    @property
    def W(self) -> float:
        """
        Average time IN THE SYSTEM (waiting + service).
        Formula: W = Wq + 1/μ
        """
        if not self.is_stable:
            return float('inf')
        return self.Wq + (1 / self.mu)

    @property
    def L(self) -> float:
        """
        Average number of customers IN THE SYSTEM.
        Using Little's Law: L = λ * W
        """
        if not self.is_stable:
            return float('inf')
        return self.lam * self.W

    def results(self) -> dict:
        """
        Returns all computed metrics as a dictionary.
        """
        return {
            "model":             "M/M/c",
            "arrival_rate":      self.lam,
            "service_rate":      self.mu,
            "num_servers":       self.c,
            "utilization":       self.rho,
            "is_stable":         self.is_stable,
            "erlang_c":          self._erlang_c(),
            "L_system":          self.L,
            "L_queue":           self.Lq,
            "W_system":          self.W,
            "W_queue":           self.Wq,
        }
