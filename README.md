# 🎓 Smart Campus Queue & Resource Optimization System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=for-the-badge&logo=python&logoColor=white)
![Operations Research](https://img.shields.io/badge/Operations-Research-green?style=for-the-badge)

**A mini project for Operations Research / Optimisation Techniques**

*Simulates and optimizes queue behavior in real-world campus scenarios like canteens, libraries, and service counters using classical Queueing Theory.*

</div>

---

## 📸 Preview

| M/M/1 Analysis | Time Simulation | Charts |
|:-:|:-:|:-:|
| Single server metrics | Peak vs off-peak comparison | Wq vs arrival rate |

---

## 🚀 Features

- ✅ **M/M/1 Queue Model** — Single server analysis (utilization, L, Lq, W, Wq, P0)
- ✅ **M/M/c Queue Model** — Multi-server analysis using the Erlang C formula
- ✅ **Smart Suggestion Engine** — Threshold-based advice on staffing
- ✅ **Time-Period Simulation** — Peak vs. off-peak hour comparison for canteen, library, service counter
- ✅ **Arrival Rate Sweep** — Sensitivity analysis showing nonlinear queue growth near saturation
- ✅ **Server Count Comparison** — Find the minimum servers needed for stable performance
- ✅ **Interactive Web UI** — Built with Streamlit (sliders, live metrics, embedded charts)
- ✅ **Matplotlib Visualizations** — Wq vs λ, full dashboard, peak/non-peak bar charts

---

## 📁 Project Structure

```
Optimisation_Technique_Mini_Project/
│
├── app.py              ← Streamlit web frontend (run this for the UI)
├── main.py             ← Terminal-based interactive menu
├── queue_model.py      ← Core math: MM1Queue and MMCQueue classes
├── simulation.py       ← Scenarios: time-period, sweep, server comparison
├── visualizer.py       ← Matplotlib chart generators
├── utils.py            ← Display helpers, smart suggestion engine
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the repository
```bash
git clone https://github.com/abi-shek-dev/Optimisation_Technique_Mini_Project.git
cd Optimisation_Technique_Mini_Project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Web UI (Recommended)
```bash
streamlit run app.py
```
Opens automatically at `http://localhost:8501`

### 4. OR Run the Terminal Menu
```bash
python main.py
```

---

## 📐 Theory — Queueing Models

### M/M/1 Queue (Single Server)

| Metric | Formula | Meaning |
|--------|---------|---------|
| Utilization `ρ` | `λ / μ` | Fraction of time server is busy |
| Avg in system `L` | `ρ / (1 - ρ)` | Customers waiting + being served |
| Avg in queue `Lq` | `ρ² / (1 - ρ)` | Customers waiting only |
| Avg time in system `W` | `1 / (μ - λ)` | Total time per customer |
| Avg wait time `Wq` | `λ / (μ(μ - λ))` | Queue wait time per customer |
| Server idle prob. `P0` | `1 - ρ` | Probability server is free |

> **Stability condition:** `λ < μ`
>
> **Little's Law:** `L = λ × W` and `Lq = λ × Wq`

### M/M/c Queue (Multi-Server)

Uses the **Erlang C formula** to compute the probability that an arriving customer must wait (all `c` servers busy), then derives `Lq`, `Wq`, `W`, and `L`.

> **Stability condition:** `λ < c × μ`

---

## 💡 Smart Suggestion Thresholds

| Utilization (ρ) | Status | Recommendation |
|-----------------|--------|----------------|
| ρ > 80% | 🔴 HIGH LOAD | Add more servers immediately |
| 50% < ρ ≤ 80% | 🟡 MODERATE | Monitor during peak hours |
| ρ ≤ 50% | 🟢 EFFICIENT | Consider reducing servers off-peak |

---

## 🏫 Campus Scenarios

| Location | Time Period | λ | μ | Status |
|----------|------------|---|---|--------|
| Canteen | Lunch Hour (1-2 PM) | 45 | 15 | 🔴 Overloaded (needs 4+ servers) |
| Canteen | Early Morning (7-9 AM) | 5 | 10 | 🟢 Efficient |
| Library | Exam Week Afternoon | 25 | 8 | 🔴 Overloaded |
| Service Counter | Mid-Morning (11AM-1PM) | 28 | 15 | 🟡 Moderate |

---

## 🎓 Subject Context

- **Subject:** Operations Research / Optimisation Techniques
- **Topic:** Queueing Theory (M/M/1, M/M/c models)
- **Reference:** Hillier & Lieberman — *Introduction to Operations Research*
- **Key Concepts:** Little's Law, Erlang C Formula, Utilization Factor, Stability Condition

---

## 🌟 Possible Extensions

- [ ] M/M/1/K — Finite capacity queue (limited waiting room)
- [ ] Priority Queues — Different customer classes (faculty vs. students)
- [ ] Cost Optimization — Minimize (server cost + customer waiting cost)
- [ ] Discrete-Event Simulation — Using SimPy for stochastic modeling
- [ ] M/G/1 Queue — General (non-exponential) service distributions
- [ ] Real Data Input — Read λ/μ from CSV footfall records

---

## 👨‍💻 Author

**Abhishek** — College Mini Project, Operations Research
GitHub: [@abi-shek-dev](https://github.com/abi-shek-dev)

---

<div align="center">
  Made with ❤️ for Operations Research
</div>
