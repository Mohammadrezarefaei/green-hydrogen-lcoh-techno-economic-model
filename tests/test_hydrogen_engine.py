"""Automated Pytest Suite for PEM Electrolyzer LCOH Engine."""

import pytest
from src.hydrogen_engine import HydrogenTechnoEconomicEngine


def test_lcoh_calculation_positive_and_coherent():
  engine = HydrogenTechnoEconomicEngine(
      electrolyzer_capacity_mwe=20.0,
      capex_eur_per_kw=1100.0,
      wacc=0.07,
      project_lifetime_years=20,
  )
  # 8,760 hours of synthetic power price profile
  spot_prices = [35.0 if (i % 24 >= 10 and i % 24 <= 16) else 80.0 for i in range(8760)]

  res = engine.simulate_dispatch_and_lcoh(spot_prices, h2_offtake_price_eur_kg=6.50)

  assert res["lcoh_total_eur_kg"] > 0.0
  assert res["annual_operating_flh"] > 0
  assert res["annual_h2_produced_tons"] > 0.0
  # Sum of components must roughly equal total LCOH
  sum_components = (
      res["lcoh_capex_share"]
      + res["lcoh_electricity_share"]
      + res["lcoh_fixed_opex_share"]
      + res["lcoh_stack_share"]
      + res["lcoh_water_share"]
  )
  assert abs(res["lcoh_total_eur_kg"] - sum_components) <= 0.05


def test_economic_gate_suppresses_high_cost_hours():
  engine = HydrogenTechnoEconomicEngine(
      electrolyzer_capacity_mwe=10.0,
      specific_consumption_kwh_kg=50.0,
      grid_fees_taxes_eur_mwh=10.0,
  )
  # Prices well above any reasonable willing-to-pay threshold for €3/kg H2
  expensive_prices = [300.0] * 8760

  with pytest.raises(ValueError, match="Electrolyzer never operated"):
    engine.simulate_dispatch_and_lcoh(expensive_prices, h2_offtake_price_eur_kg=3.0)
