"""
Techno-Economic & Economic Dispatch Engine for PEM Electrolyzers.
Calculates 8,760-hour operations, Discounted Cash Flow (DCF), and LCOH (€/kg H2).
"""

from typing import Dict, List
import numpy as np


class HydrogenTechnoEconomicEngine:

  def __init__(
      self,
      electrolyzer_capacity_mwe: float = 20.0,
      capex_eur_per_kw: float = 1100.0,
      specific_consumption_kwh_kg: float = 52.5,
      water_consumption_l_kg: float = 10.0,
      water_cost_eur_m3: float = 2.50,
      fixed_opex_pct_capex: float = 0.03,
      stack_replacement_year: int = 8,
      stack_replacement_cost_pct: float = 0.30,
      wacc: float = 0.07,
      project_lifetime_years: int = 20,
      grid_fees_taxes_eur_mwh: float = 15.0,
  ):
    self.capacity_mwe = electrolyzer_capacity_mwe
    self.total_capex = electrolyzer_capacity_mwe * 1000.0 * capex_eur_per_kw
    self.specific_consumption = specific_consumption_kwh_kg
    self.water_consumption = water_consumption_l_kg
    self.water_cost_m3 = water_cost_eur_m3
    self.annual_fixed_opex = self.total_capex * fixed_opex_pct_capex
    self.stack_replacement_year = stack_replacement_year
    self.stack_replacement_cost = (
        self.total_capex * stack_replacement_cost_pct
    )
    self.wacc = wacc
    self.lifetime_years = project_lifetime_years
    self.grid_fees = grid_fees_taxes_eur_mwh

  def simulate_dispatch_and_lcoh(
      self,
      spot_prices_eur_mwh: List[float],
      h2_offtake_price_eur_kg: float = 6.50,
  ) -> Dict[str, float]:
    """Runs 8,760h economic gate dispatch, DCF modeling, and returns LCOH component metrics."""
    spot_prices = np.array(spot_prices_eur_mwh)
    effective_power_price = spot_prices + self.grid_fees

    # Economic willingness-to-pay threshold per MWh
    var_water_cost_per_kg = (
        self.water_consumption / 1000.0
    ) * self.water_cost_m3
    max_power_price_eur_mwh = (
        h2_offtake_price_eur_kg - var_water_cost_per_kg
    ) / (self.specific_consumption / 1000.0)

    # Dispatch: Operate when delivered power cost <= Willingness-to-pay
    is_operating = effective_power_price <= max_power_price_eur_mwh
    power_drawn_mw = np.where(is_operating, self.capacity_mwe, 0.0)
    hourly_h2_kg = np.where(
        is_operating,
        (self.capacity_mwe * 1000.0) / self.specific_consumption,
        0.0,
    )

    annual_operating_hours = int(np.sum(is_operating))
    annual_h2_kg = float(np.sum(hourly_h2_kg))
    annual_power_mwh = float(np.sum(power_drawn_mw))
    annual_elec_cost = float(np.sum(power_drawn_mw * effective_power_price))
    annual_water_cost = float(np.sum(hourly_h2_kg * var_water_cost_per_kg))
    annual_var_opex = annual_elec_cost + annual_water_cost

    if annual_h2_kg <= 0:
      raise ValueError(
          "Electrolyzer never operated: electricity prices exceed economic"
          " threshold."
      )

    # Discounted Cash Flow (DCF) Valuation
    discount_factors = np.array([
        (1.0 + self.wacc) ** (-t) for t in range(self.lifetime_years + 1)
    ])

    cash_outflows = np.zeros(self.lifetime_years + 1)
    cash_outflows[0] = self.total_capex
    for yr in range(1, self.lifetime_years + 1):
      total_opex = self.annual_fixed_opex + annual_var_opex
      if yr == self.stack_replacement_year:
        total_opex += self.stack_replacement_cost
      cash_outflows[yr] = total_opex

    discounted_h2_vector = np.zeros(self.lifetime_years + 1)
    discounted_h2_vector[1:] = annual_h2_kg

    npv_costs = np.sum(cash_outflows * discount_factors)
    npv_h2_kg = np.sum(discounted_h2_vector * discount_factors)
    lcoh_total = float(npv_costs / npv_h2_kg)

    # Breakdown components
    crf = (self.wacc * (1.0 + self.wacc) ** self.lifetime_years) / (
        ((1.0 + self.wacc) ** self.lifetime_years) - 1.0
    )
    lcoh_capex = float((self.total_capex * crf) / annual_h2_kg)
    lcoh_electricity = float(annual_elec_cost / annual_h2_kg)
    lcoh_fixed_opex = float(self.annual_fixed_opex / annual_h2_kg)
    lcoh_stack = float(
        (
            self.stack_replacement_cost
            * ((1.0 + self.wacc) ** (-self.stack_replacement_year))
            * crf
        )
        / annual_h2_kg
    )
    lcoh_water_other = float(
        lcoh_total
        - (lcoh_capex + lcoh_electricity + lcoh_fixed_opex + lcoh_stack)
    )

    return {
        "lcoh_total_eur_kg": round(lcoh_total, 2),
        "lcoh_capex_share": round(lcoh_capex, 2),
        "lcoh_electricity_share": round(lcoh_electricity, 2),
        "lcoh_fixed_opex_share": round(lcoh_fixed_opex, 2),
        "lcoh_stack_share": round(lcoh_stack, 2),
        "lcoh_water_share": round(lcoh_water_other, 2),
        "annual_operating_flh": annual_operating_hours,
        "annual_h2_produced_tons": round(annual_h2_kg / 1000.0, 1),
        "avg_electricity_cost_eur_mwh": round(
            annual_elec_cost / annual_power_mwh, 2
        ),
    }
