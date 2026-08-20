"""Streamlit Web App: Green Hydrogen Techno-Economic & LCOH Valuation Model."""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.hydrogen_engine import HydrogenTechnoEconomicEngine

st.set_page_config(
    page_title="Green Hydrogen LCOH & Electrolyzer Valuation",
    page_icon="💧",
    layout="wide"
)

st.title("💧⚡ Green Hydrogen & PEM Electrolyzer LCOH Model")
st.markdown("Techno-economic asset valuation, **8,760-hour spot price dispatch gate**, and **Levelized Cost of Hydrogen (LCOH)** modeling.")

# Sidebar Configurations
st.sidebar.header("⚙️ Technical & CAPEX Parameters")
capacity_mw = st.sidebar.slider("Electrolyzer Capacity (MWe)", 5.0, 100.0, 20.0, 5.0)
capex_kw = st.sidebar.slider("Installed CAPEX (€/kWe)", 600.0, 2000.0, 1100.0, 50.0)
efficiency_kwh_kg = st.sidebar.slider("Specific Consumption (kWh/kg H2)", 48.0, 60.0, 52.5, 0.5)
wacc_pct = st.sidebar.slider("WACC / Discount Rate (%)", 4.0, 12.0, 7.0, 0.5) / 100.0

st.sidebar.header("📈 Market & Operational Rules")
offtake_price = st.sidebar.slider("H2 Target Offtake Price (€/kg)", 3.0, 10.0, 6.5, 0.25)
grid_fee = st.sidebar.slider("Grid Fees & Levies (€/MWh)", 0.0, 40.0, 15.0, 1.0)
stack_yr = st.sidebar.slider("Stack Replacement Interval (Years)", 5, 12, 8, 1)

# Generate 8,760h Synthetic Spot Price Series
np.random.seed(42)
hours_arr = np.arange(8760)
base_spot = 45.0 + 25.0 * np.sin(2 * np.pi * hours_arr / 8760)
daily_cycle = 20.0 * np.sin(2 * np.pi * (hours_arr % 24 - 6) / 24)
volatility = np.random.normal(0, 30.0, 8760)
solar_dip = np.where((hours_arr % 24 >= 10) & (hours_arr % 24 <= 16), -35.0, 0.0)
spot_prices = np.clip(base_spot + daily_cycle + volatility + solar_dip, -30.0, 250.0).tolist()

engine = HydrogenTechnoEconomicEngine(
    electrolyzer_capacity_mwe=capacity_mw,
    capex_eur_per_kw=capex_kw,
    specific_consumption_kwh_kg=efficiency_kwh_kg,
    wacc=wacc_pct,
    grid_fees_taxes_eur_mwh=grid_fee,
    stack_replacement_year=stack_yr
)

try:
    results = engine.simulate_dispatch_and_lcoh(spot_prices, h2_offtake_price_eur_kg=offtake_price)
    
    col1, col2 = st.columns([1.8, 1])

    with col1:
        st.subheader("📊 LCOH Cost Breakdown Waterfall")
        categories = ["Electricity", "Initial CAPEX", "Fixed OPEX", "Stack Replacement", "Water & Consumables"]
        shares = [
            results["lcoh_electricity_share"],
            results["lcoh_capex_share"],
            results["lcoh_fixed_opex_share"],
            results["lcoh_stack_share"],
            results["lcoh_water_share"]
        ]
        colors = ["#F59E0B", "#2563EB", "#64748B", "#8B5CF6", "#06B6D4"]

        fig, ax = plt.subplots(figsize=(9, 4.8))
        bars = ax.barh(categories, shares, color=colors, alpha=0.85)
        ax.set_xlabel("Cost Contribution [€ / kg H2]", fontweight="bold")
        ax.set_title(f"Levelized Cost of Hydrogen: €{results['lcoh_total_eur_kg']:.2f} / kg H2", fontsize=11, fontweight="bold")
        ax.grid(True, linestyle=":", alpha=0.6)

        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.05, bar.get_y() + bar.get_height()/2, f"€{width:.2f}", va='center', ha='left', fontsize=9, fontweight="bold")

        ax.invert_yaxis()
        st.pyplot(fig)

    with col2:
        st.subheader("💶 Asset Performance Metrics")
        st.metric("Total LCOH", f"€{results['lcoh_total_eur_kg']:.2f} / kg H2")
        st.metric("Annual Production", f"{results['annual_h2_produced_tons']:,.1f} Metric Tons / yr")
        st.metric("Annual Full Load Hours (FLH)", f"{results['annual_operating_flh']:,} h / 8,760 h")
        st.metric("Avg Delivered Power Cost", f"€{results['avg_electricity_cost_eur_mwh']:.2f} / MWh")

except ValueError as e:
    st.error(f"Error: {e}")
