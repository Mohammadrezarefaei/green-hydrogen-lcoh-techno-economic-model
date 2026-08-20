# 💧⚡ Green Hydrogen & PEM Electrolyzer Techno-Economic Model

[![CI Pipeline](https://img.shields.io/badge/CI%20Pipeline-passing-brightgreen?logo=github&style=flat-square)](https://github.com/Mohammadrezarefaei/green-hydrogen-lcoh-techno-economic-model/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://green-hydrogen-lcoh-techno-economic-model-schxqnqzapdz7gchujmf.streamlit.app/)

A techno-economic valuation framework and **8,760-hour economic dispatch model** for megawatt-scale PEM electrolyzers, evaluating **Levelized Cost of Hydrogen (LCOH)** under volatile EPEX Spot electricity prices, CAPEX amortization, and stack degradation dynamics.

---

## 🚀 Live Interactive Demo
👉 **[Access the Live Streamlit Web App](https://green-hydrogen-lcoh-techno-economic-model-schxqnqzapdz7gchujmf.streamlit.app/)**

---

## 📌 Economic Dispatch Logic & LCOH Formulation

Electrolyzer utilization is optimized on an hourly basis by evaluating the marginal cost of delivered electricity against the maximum economic willingness-to-pay derived from industrial off-take contracts:

* **Hourly Dispatch Gate:**
  $$\text{Operate} \iff P_{\text{Spot}}(t) + \text{Fees}_{\text{Grid}} \le \frac{\text{Price}_{\text{Offtake}} - C_{\text{Water}}}{\text{Specific Consumption (kWh/kg)}} \times 1000$$

* **Levelized Cost of Hydrogen (Discounted Cash Flow):**
  $$\text{LCOH} = \frac{\sum_{t=0}^{N} \frac{\text{CAPEX}_t + \text{OPEX}_t + \text{Stack}_t}{(1 + \text{WACC})^t}}{\sum_{t=1}^{N} \frac{\text{Production}_t (\text{kg})}{(1 + \text{WACC})^t}}$$

---

## 🔍 Key Findings & Techno-Economic Takeaways

* **Electricity Cost Dominance:** Power procurement accounts for 55–70% of total LCOH, making dynamic operational gating during high-price peak hours essential.
* **Full Load Hours (FLH) vs. CAPEX Trade-off:** Increasing operating hours reduces CAPEX amortization per kg of $H_2$, but running during high-price power windows rapidly erodes operating margins.
* **Stack Replacement Provisioning:** Incorporates mid-life PEM stack replacement (~Year 8) discounted into project lifecycle economics.

---

## 🛠️ Software Architecture & Automated Testing
* **CI/CD Pipeline:** Automated GitHub Actions workflows running a full `pytest` suite validating economic dispatch triggers, DCF cash flow integrity, and LCOH component consistency.
* **Modular Core Engine:** Implemented in `src/hydrogen_engine.py`.
* **Tech Stack:** Python 3.11, NumPy, Pandas, Matplotlib, Streamlit, Pytest.
