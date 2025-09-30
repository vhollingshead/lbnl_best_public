import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.save_progress import load_progress_json, get_user_data_dir
import re

import platform
import os

import subprocess
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'svg'

import textwrap
from PyQt6.QtWidgets import QMessageBox

# Default Values and Input Field Mapping
page2_formal_to_qt_mapping = {
    # Electricity
    "Cost of electricity": "electricity_input",
    "Cost of electricity unit": "comboBox_electricity_unit",

    # Fuel costs
    "Cost of fuel.coal": "coal_input",
    "Cost of fuel.coke": "coke_input",
    "Cost of fuel.natural gas": "natural_gas_input",
    "Cost of fuel.biomass": "biomass_input",
    "Cost of fuel.municipal wastes": "municipal_wastes_input",

    # Fuel units
    "Cost of fuel unit.coal": "comboBox_coal_unit",
    "Cost of fuel unit.coke": "comboBox_coke_unit",
    "Cost of fuel unit.natural gas": "comboBox_natural_gas_unit",
    "Cost of fuel unit.biomass": "comboBox_biomass_unit",
    "Cost of fuel unit.municipal wastes": "comboBox_municipal_wastes_unit",

    # CO2 pricing & emissions
    "Carbon price ($/tCO2)": "carbon_price_input",
    "Grid CO2 emission intensity (tCO2/MWh)": "grid_co2_input",
    "Process emission per metric ton of clinker (tCO2/t clinker)": "process_emission_per_metric_input",

    # Emission intensities
    "Fuel CO2 intensity (tCO2/TJ).coal": "coal_emission_intensity_input",
    "Fuel CO2 intensity (tCO2/TJ).coke": "coke_emission_intensity_input",
    "Fuel CO2 intensity (tCO2/TJ).natural gas": "natural_gas_emission_intensity_input",
    "Fuel CO2 intensity (tCO2/TJ).biomass": "biomass_emission_intensity_input",
    "Fuel CO2 intensity (tCO2/TJ).municipal wastes": "municipal_wastes_emission_intensity_input",

    # Heating values
    "Fuel high heating value (MJ/kg fuel).coal": "coal_hhv_input",
    "Fuel high heating value (MJ/kg fuel).coke": "coke_hhv_input",
    "Fuel high heating value (MJ/kg fuel).natural gas": "natural_gas_hhv_input",
    "Fuel high heating value (MJ/kg fuel).biomass": "biomass_hhv_input",
    "Fuel high heating value (MJ/kg fuel).municipal wastes": "municipal_wastes_hvv_input"
}



## Calculations
def convert_energy_units(input_unit, input_value, HHV_value, output_unit):
    output_value = 0
    if input_unit == "$/kgce":
        output_value = input_value/29.308
    elif input_unit == "$/tce":
        output_value = input_value/29308
    elif input_unit == "$/GJ":
        output_value = input_value/1000
    elif input_unit == "$/MJ":
        output_value = input_value
    elif input_unit == "$/MMBtu":
        output_value = input_value/1054.35
    elif input_unit == "$/kg":
        output_value = input_value/HHV_value
    elif input_unit == "$/metric ton":
        output_value = 0.01*input_value/HHV_value
    elif input_unit == "$/Mcf":
        output_value = input_value/1094.052
    elif input_unit == "$/kWh":
        output_value = input_value/3.6
    elif input_unit == "$/MWh":
        output_value = input_value/(3.6*1000)
    else:
        output_value = np.nan
    
    if output_unit == "$/MJ":
        output_value = output_value
    elif output_unit == "$/kWh":
        output_value = output_value*3.6
    
    return output_value

def _f(x, d=0.0):
    sci_pattern = re.compile(r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$')
    
    try:
        s = str(x).strip().replace(",", "")
        if sci_pattern.match(s):
            return float(s)
        return d
    except Exception:
        return d

def Page2_Costs_and_Emissions_Input_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)
    filepath = json_folder / "Cost_and_Emission_Input.json"

    # Page 2 - Cost and Emission Input
    cost_and_emissions_dict = {
        "name": "Cost and Emission Input",
        "Cost of electricity": 0.2,
        "Cost of electricity unit": "$/kWh",
        "Cost of fuel": {
            "coal": 100.0,
            "coke": 180.0,
            "natural gas": 6.0,
            "biomass": 40.0,
            "municipal wastes": 40.0
        },
        "Cost of fuel unit": {
            "coal": "$/metric ton",
            "coke": "$/metric ton",
            "natural gas": "$/MMBtu",
            "biomass": "$/metric ton",
            "municipal wastes": "$/metric ton"
        },
        "Carbon price ($/tCO2)": 20.0,
        "Grid CO2 emission intensity (tCO2/MWh)": 0.5,
        "Fuel CO2 intensity (tCO2/TJ)": {
            "coal": 93,
            "coke": 95,
            "natural gas": 56,
            "biomass": 0,
            "municipal wastes": 0
        },
        "Fuel high heating value (MJ/kg fuel)": {
            "coal": 30.0,
            "coke": 26.0,
            "natural gas": 52.0,
            "biomass": 20.0,
            "municipal wastes": 22.0
        },
        "Cost of electricity in $/kWh": 0.2,
        "Cost of fuel in $/MJ": {
            "coal": 0.03333333333333333,
            "coke": 0.06923076923076923,
            "natural gas": 0.00569070991606203,
            "biomass": 0.02,
            "municipal wastes": 0.018181818181818184
        },
        "Process emission per metric ton of clinker (tCO2/t clinker)": 0.507} 

    # Cost of Electricity
    if self.ui.electricity_input.text() != "":
        cost_and_emissions_dict["Cost of electricity"] = _f(self.ui.electricity_input.text())

    if self.ui.comboBox_electricity_unit.currentText() != "Select electricity unit here":
        cost_and_emissions_dict["Cost of electricity unit"] = self.ui.comboBox_electricity_unit.currentText()
    if cost_and_emissions_dict["Cost of electricity"] != "":
        cost_and_emissions_dict["Cost of electricity in $/kWh"] = convert_energy_units(cost_and_emissions_dict["Cost of electricity unit"], cost_and_emissions_dict["Cost of electricity"], "NA", "$/kWh")

    # Cost of Fuel
    if self.ui.coal_input.text() != "":
        cost_and_emissions_dict["Cost of fuel"]["coal"] = _f(self.ui.coal_input.text())
    if self.ui.coke_input.text() != "":
        cost_and_emissions_dict["Cost of fuel"]["coke"] = _f(self.ui.coke_input.text())
    if self.ui.natural_gas_input.text() != "":
        cost_and_emissions_dict["Cost of fuel"]["natural gas"] = _f(self.ui.natural_gas_input.text())
    if self.ui.biomass_input.text() != "":
        cost_and_emissions_dict["Cost of fuel"]["biomass"] = _f(self.ui.biomass_input.text())
    if self.ui.municipal_wastes_input.text() != "":
        cost_and_emissions_dict["Cost of fuel"]["municipal wastes"] = _f(self.ui.municipal_wastes_input.text())

    # Cost of Fuel Unit
    if self.ui.comboBox_coal_unit.currentText() != "Select fuel unit here":
        cost_and_emissions_dict["Cost of fuel unit"]["coal"] = self.ui.comboBox_coal_unit.currentText()
    if self.ui.comboBox_coke_unit.currentText() != "Select fuel unit here":
        cost_and_emissions_dict["Cost of fuel unit"]["coke"] = self.ui.comboBox_coke_unit.currentText()
    if self.ui.comboBox_natural_gas_unit.currentText() != "Select fuel unit here":
        cost_and_emissions_dict["Cost of fuel unit"]["natural gas"] = self.ui.comboBox_natural_gas_unit.currentText()
    if self.ui.comboBox_biomass_unit.currentText() != "Select fuel unit here":
        cost_and_emissions_dict["Cost of fuel unit"]["biomass"] = self.ui.comboBox_biomass_unit.currentText()
    if self.ui.comboBox_municipal_wastes_unit.currentText() != "Select fuel unit here":
        cost_and_emissions_dict["Cost of fuel unit"]["municipal wastes"] = self.ui.comboBox_municipal_wastes_unit.currentText()

    # Carbon Price
    if self.ui.carbon_price_input.text() != "":
        cost_and_emissions_dict["Carbon price ($/tCO2)"] = _f(self.ui.carbon_price_input.text())

    # Grid CO2 Emission Intensity
    if self.ui.grid_co2_input.text() != "":
        cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"] = _f(self.ui.grid_co2_input.text())

    # High Heating Values
    if self.ui.coal_hhv_input.text() != "":
        cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["coal"] = _f(self.ui.coal_hhv_input.text())
    if self.ui.coke_hhv_input.text() != "":
        cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["coke"] = _f(self.ui.coke_hhv_input.text())
    if self.ui.natural_gas_hhv_input.text() != "":
        cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["natural gas"] = _f(self.ui.natural_gas_hhv_input.text())
    if self.ui.biomass_hhv_input.text() != "":
        cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["biomass"] = _f(self.ui.biomass_hhv_input.text())
    if self.ui.municipal_wastes_hvv_input.text() != "":
        cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["municipal wastes"] = _f(self.ui.municipal_wastes_hvv_input.text())

    # Calculate High Heating Values
    cost_and_emissions_dict["Cost of fuel in $/MJ"]["coal"] = convert_energy_units(cost_and_emissions_dict["Cost of fuel unit"]["coal"], cost_and_emissions_dict["Cost of fuel"]["coal"], cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["coal"], "$/MJ")
    cost_and_emissions_dict["Cost of fuel in $/MJ"]["coke"] = convert_energy_units(cost_and_emissions_dict["Cost of fuel unit"]["coke"], cost_and_emissions_dict["Cost of fuel"]["coke"], cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["coke"], "$/MJ")
    cost_and_emissions_dict["Cost of fuel in $/MJ"]["natural gas"] = convert_energy_units(cost_and_emissions_dict["Cost of fuel unit"]["natural gas"], cost_and_emissions_dict["Cost of fuel"]["natural gas"], cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["natural gas"], "$/MJ")
    cost_and_emissions_dict["Cost of fuel in $/MJ"]["biomass"] = convert_energy_units(cost_and_emissions_dict["Cost of fuel unit"]["biomass"], cost_and_emissions_dict["Cost of fuel"]["biomass"], cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["biomass"], "$/MJ")
    cost_and_emissions_dict["Cost of fuel in $/MJ"]["municipal wastes"] = convert_energy_units(cost_and_emissions_dict["Cost of fuel unit"]["municipal wastes"], cost_and_emissions_dict["Cost of fuel"]["municipal wastes"], cost_and_emissions_dict["Fuel high heating value (MJ/kg fuel)"]["municipal wastes"], "$/MJ")

    # Process Emission Per Metric
    if self.ui.process_emission_per_metric_input.text() != "":
        cost_and_emissions_dict["Process Emission Per Metric"] = _f(self.ui.process_emission_per_metric_input.text())

    # Save the updated dictionary
    with open(filepath, "w") as f:
        json.dump(cost_and_emissions_dict, f, indent=4)

    return cost_and_emissions_dict

def Page3_Production_Input_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)
    filepath = json_folder / "Production_Input.json"

    production_input_dict = {
    "name": "Production Input",
    "Amount of limestone used per year (tonnes/year)": 150000.0,
    "Amount of gypsum used per year (tonnes/year)": 0.0,
    "Amount of calcined clay used per year (tonnes/year)": 0.0,
    "Amount of blast furnace slag used per year (tonnes/year)": 10000.0,
    "Amount of other slag used per year (tonnes/year)": 0.0,
    "Amount of fly ash used per year (tonnes/year)": 100000.0,
    "Amount of other natural pozzolans used per year (tonnes/year)": 10000.0,
    "Amount of raw materials preblended": 270000.0,
    "Amount of raw materials crushed": 270000.0,
    "Amount of additives dried": 10000.0,
    "Amount of additives ground": 120000.0,
    "Kiln - Clinker Production": {
        "Type 1": {
            "Type": "NSP",
            "Production (tonnes/year)": 50000.0
        },
        "Type 2": {
            "Type": "pre-heater",
            "Production (tonnes/year)": 50000.0
        }
    },
    "Total clinker production": 100000.0,
    "Cement production": {
        "Pure Portland cement production (tonnes/year)": 0.0,
        "Common Portland cement production (tonnes/year)": 0.0,
        "Slag cement production (tonnes/year)": 75000.0,
        "Fly ash cement production (tonnes/year)": 50000.0,
        "Pozzolana cement production (tonnes/year)": 0.0,
        "Blended cement production (tonnes/year)": 0.0
    },
    "Total cement production (tonnes/year)": 0,
    "Clinker to cement ratio": 0.8
}
    
    # Clinker Material Produced per Year
    if self.ui.limestone_input.text() != "":
        production_input_dict["Amount of limestone used per year (tonnes/year)"] = _f(self.ui.limestone_input.text())
    if self.ui.gypsum_input.text() != "":
        production_input_dict["Amount of gypsum used per year (tonnes/year)"] = _f(self.ui.gypsum_input.text())
    if self.ui.calcined_clay_input.text() != "":
        production_input_dict["Amount of calcined clay used per year (tonnes/year)"] = _f(self.ui.calcined_clay_input.text())
    if self.ui.blast_furnace_slag_input.text() != "":
        production_input_dict["Amount of blast furnace slag used per year (tonnes/year)"] = _f(self.ui.blast_furnace_slag_input.text())
    if self.ui.other_slag_input.text() != "":
        production_input_dict["Amount of other slag used per year (tonnes/year)"] = _f(self.ui.other_slag_input.text())
    if self.ui.fly_ash_input.text() != "":
        production_input_dict["Amount of fly ash used per year (tonnes/year)"] = _f(self.ui.fly_ash_input.text())
    if self.ui.natural_pozzolans_input.text() != "":
        production_input_dict["Amount of other natural pozzolans used per year (tonnes/year)"] = _f(self.ui.natural_pozzolans_input.text())
        
        
    # Kiln - Clinker Production
    if self.ui.type_1_input.text() != "":
        production_input_dict["Kiln - Clinker Production"]["Type 1"]["Type"] = self.ui.type_1_input.text()
    if self.ui.type_2_input.text() != "":
        production_input_dict["Kiln - Clinker Production"]["Type 2"]["Type"] = self.ui.type_2_input.text()

    if self.ui.production_1_input.text() != "":
        production_input_dict["Kiln - Clinker Production"]["Type 1"]["Production (tonnes/year)"] = _f(self.ui.production_1_input.text())
    if self.ui.production_2_input.text() != "":
        production_input_dict["Kiln - Clinker Production"]["Type 2"]["Production (tonnes/year)"] = _f(self.ui.production_2_input.text())
    
    production_input_dict["Total clinker production"] = production_input_dict["Kiln - Clinker Production"]["Type 1"]["Production (tonnes/year)"] + production_input_dict["Kiln - Clinker Production"]["Type 2"]["Production (tonnes/year)"]

    
    # Cement Production

    if self.ui.pure_portland_cement_production_input.text() != "":
        production_input_dict["Cement production"]["Pure Portland cement production (tonnes/year)"] = _f(self.ui.pure_portland_cement_production_input.text())
    if self.ui.common_portland_cement_production_input.text() != "":
        production_input_dict["Cement production"]["Common Portland cement production (tonnes/year)"] = _f(self.ui.common_portland_cement_production_input.text())
    if self.ui.slag_cement_production_input.text() != "":
        production_input_dict["Cement production"]["Slag cement production (tonnes/year)"] = _f(self.ui.slag_cement_production_input.text())
    if self.ui.fly_ash_cement_production_input.text() != "":
        production_input_dict["Cement production"]["Fly ash cement production (tonnes/year)"] = _f(self.ui.fly_ash_cement_production_input.text())
    if self.ui.pozzolana_cement_production_input.text() != "":
        production_input_dict["Cement production"]["Pozzolana cement production (tonnes/year)"] = _f(self.ui.pozzolana_cement_production_input.text())
    if self.ui.blended_cement_production_input.text() != "":
        production_input_dict["Cement production"]["Blended cement production (tonnes/year)"] = _f(self.ui.blended_cement_production_input.text())

    Total_raw_material_and_additive = production_input_dict["Amount of limestone used per year (tonnes/year)"] + production_input_dict["Amount of gypsum used per year (tonnes/year)"] + production_input_dict["Amount of calcined clay used per year (tonnes/year)"] + production_input_dict["Amount of blast furnace slag used per year (tonnes/year)"] + production_input_dict["Amount of other slag used per year (tonnes/year)"] + production_input_dict["Amount of fly ash used per year (tonnes/year)"] + production_input_dict["Amount of other natural pozzolans used per year (tonnes/year)"]

    production_input_dict["Amount of raw materials preblended"] = Total_raw_material_and_additive
    production_input_dict["Amount of raw materials crushed"] = Total_raw_material_and_additive
    production_input_dict["Amount of additives dried"] = production_input_dict["Amount of blast furnace slag used per year (tonnes/year)"] + production_input_dict["Amount of other slag used per year (tonnes/year)"]
    production_input_dict["Amount of additives ground"] = production_input_dict["Amount of blast furnace slag used per year (tonnes/year)"] + production_input_dict["Amount of other slag used per year (tonnes/year)"] + production_input_dict["Amount of fly ash used per year (tonnes/year)"] + production_input_dict["Amount of other natural pozzolans used per year (tonnes/year)"]

    Total_clinker = 0
    for kiln_type in production_input_dict["Kiln - Clinker Production"].keys():
        Total_clinker += production_input_dict["Kiln - Clinker Production"][kiln_type]["Production (tonnes/year)"]
    production_input_dict["Total clinker production"] = Total_clinker

    Total_cement = 0
    for cement_type in production_input_dict["Cement production"].keys():
        Total_cement += production_input_dict["Cement production"][cement_type]

    production_input_dict["Clinker to cement ratio"] = Total_clinker/Total_cement
    production_input_dict["Total cement"] = Total_cement

    # Save the updated dictionary
    with open(filepath, "w") as f:
        json.dump(production_input_dict, f, indent=4)

    return production_input_dict

def Page4_Carbon_Capture_Input_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)
    filepath = json_folder / "Carbon_Capture_Input.json"

    carbon_capture_dict = {
    "name": "Carbon Capture",
    "CO2 captured (million metric tons/year)": 0.0
    }
    # Set Default Values
    Page_4_default_values = {
        "co2_captured_input": float(0)
    }

    # CO2 Captured
    if self.ui.co2_captured_input.text() != "":
        carbon_capture_dict["CO2 captured (million metric tons/year)"] = _f(self.ui.co2_captured_input.text())

    # Save the updated dictionary
    with open(filepath, "w") as f:
        json.dump(carbon_capture_dict, f, indent=4)

    return carbon_capture_dict


def Page5_ElectricityGeneration_Input_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)
    filepath = json_folder / "Electricity_Generation_Input.json"

    electricity_generation_input_dict = {
    "name": "Electricity Generation Input",
    "Total electricity purchased (kWh/year)": 18040000.0,
    "Total electricity generated onsite (kWh/year)": 1000000.0,
    "Electricity generated and sold to the grid or offsite (kWh/year)": 0.0,
    "Electricity generated and used at cement plant (kWh/year)": 1000000.0,
    "Energy used for electricity generation (MJ/year)": {
        "waste heat": 0.0,
        "coal": 10000000.0,
        "coke": 0.0,
        "natural gas": 0.0,
        "biomass": 0.0,
        "municipal wastes": 0.0
    },
    "Energy used for electricity generation (kWh/year) - onsite renewables": 0.0,
    "Subtotal final energy (MJ/year)": 10000000.0
}
    
    # Electricity Generation Input
    if self.ui.total_energy_purchased_input.text() != "":
        electricity_generation_input_dict["Total electricity purchased (kWh/year)"] = _f(self.ui.total_energy_purchased_input.text())
    if self.ui.total_electricity_generated_onsite_input.text() != "":
        electricity_generation_input_dict["Total electricity generated onsite (kWh/year)"] = _f(self.ui.total_electricity_generated_onsite_input.text())
    if self.ui.electricity_generated_input.text() != "":
        electricity_generation_input_dict["Electricity generated and sold to the grid or offsite (kWh/year)"] = _f(self.ui.electricity_generated_input.text())

        
    # Energy used for electricity generation
    if self.ui.waste_heat_input_page5.text() != "":
        electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["waste heat"] = _f(self.ui.waste_heat_input_page5.text())
    if self.ui.coal_input_page5.text() != "":
        electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coal"] = _f(self.ui.coal_input_page5.text())
    if self.ui.coke_input_page5.text() != "":
        electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coke"] = _f(self.ui.coke_input_page5.text())
    if self.ui.natural_gas_input_page5.text() != "":
        electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["natural gas"] = _f(self.ui.natural_gas_input_page5.text())
    if self.ui.biomass_input_page5.text() != "":
        electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["biomass"] = _f(self.ui.biomass_input_page5.text())
    if self.ui.municipal_wastes_input_page5.text() != "":
        electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["municipal wastes"] = _f(self.ui.municipal_wastes_input_page5.text())

    # Onsite Rewnewables
    if self.ui.onsite_renewables_input_page5.text() != "":
        electricity_generation_input_dict["Energy used for electricity generation (kWh/year) - onsite renewables"] = _f(self.ui.onsite_renewables_input_page5.text())

    # Cost and Emissions Data
    with open(json_folder / "Cost_and_Emission_Input.json", 'r') as f:
        cost_and_emissions_dict = json.load(f)

    electricity_emission_intensity = cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000 # convert to kWh # need to add emissions from electricity generation fuel, so do it later # decided to use this variable only for purchased electricity to aid indirect emissions calculations
    coal_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coal']/10**6 # convert to MJ
    coke_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coke']/10**6
    natural_gas_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['natural gas']/10**6 
    biomass_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['biomass']/10**6 
    msw_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['municipal wastes']/10**6 
    carbon_price = cost_and_emissions_dict["Carbon price ($/tCO2)"]

    electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"] = electricity_generation_input_dict["Total electricity generated onsite (kWh/year)"] - electricity_generation_input_dict["Electricity generated and sold to the grid or offsite (kWh/year)"]

    #electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]['waste heat'] = 0

    Total_electricity_fuel = sum(electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"].values())

    electricity_generation_input_dict["Subtotal final energy (MJ/year)"] = Total_electricity_fuel + electricity_generation_input_dict["Energy used for electricity generation (kWh/year) - onsite renewables"]*3.6

    electricity_fuel_emission_intensity = (electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]['waste heat']*0+ electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]['coal']*coal_emission_intensity + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]['coke']*coke_emission_intensity + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]['natural gas']*natural_gas_emission_intensity + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]['biomass']*biomass_emission_intensity + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]['municipal wastes']*msw_emission_intensity) / Total_electricity_fuel

    electricity_generation_emissions = electricity_fuel_emission_intensity * Total_electricity_fuel

    onsite_RE_electricity_generation = electricity_generation_input_dict["Energy used for electricity generation (kWh/year) - onsite renewables"]

    onsite_electricity_generation_efficiency = (electricity_generation_input_dict["Total electricity generated onsite (kWh/year)"] - onsite_RE_electricity_generation)/(Total_electricity_fuel/3.6) # this is just for generation from combustion and waste heat

    # electricity_emission_intensity = ((cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000)*electricity_generation_input_dict["Total electricity purchased (kWh/year)"] + (electricity_fuel_emission_intensity*3.6/0.305)*electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"])/(electricity_generation_input_dict["Total electricity purchased (kWh/year)"]+electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"]) # this electricity emission intensity combines both emission intensities from purchased and self-generated electricity

    ## There seems to be soem issues with the waste heat calculation. I do not trust the initial formula, which uses the waste heat of thermal electricity generation systems for waste heat for electricity generation

    electricity_generation_input_dict["Electricity Generation Emissions"] = electricity_generation_emissions
    electricity_generation_input_dict["Onsite Renewable Electricity Generation"] = onsite_RE_electricity_generation
    electricity_generation_input_dict["Electricity Fuel Emission Intensity"] = electricity_fuel_emission_intensity
    electricity_generation_input_dict["Onsite Electricity Generation Efficiency"] = onsite_electricity_generation_efficiency
    # Save the updated dictionary
    with open(filepath, "w") as f:
        json.dump(electricity_generation_input_dict, f, indent=4)


    return electricity_generation_input_dict


def Page6_Energy_Input_Default_Update_Fields(self): 
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)
    filepath = json_folder / "Energy_Input.json"

    energy_input_dict = {
    "name": "Energy Input",
    "Raw material grinding (%)": {
        "ball mill": 100.0,
        "vertical roller mill": 0.0,
        "high pressure roller press/horizontal roller mill": 0.0
    },
    "Fuel grinding (%)": {
        "ball mill": 100.0,
        "vertical rolelr mill": 0.0
    },
    "Cement grinding (%)": {
        "ball mill": 100.0,
        "vertical rolelr mill": 0.0,
        "high pressure roller press/horizontal roller mill": 0.0
    },
    "Energy input": {
        "Raw material conveying and quarraying": {
            "Production Per Process (tonnes/year)": 150000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 0.0,
            "% Electricity Consumption at production stage": 0.0,
            "Final Electricity Consumption by Process (kWh/year)": 0.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 0.0,
            "Total Primary Energy Consumption (MJ/year)": 0.0
        },
        "Preblending": {
            "Production Per Process (tonnes/year)": 270000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 350000.0,
            "% Electricity Consumption at production stage": 0.01838235294117647,
            "Final Electricity Consumption by Process (kWh/year)": 350000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 1260000.0,
            "Total Primary Energy Consumption (MJ/year)": 4131147.5409836066
        },
        "Crushing": {
            "Production Per Process (tonnes/year)": 270000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 150000.0,
            "% Electricity Consumption at production stage": 0.007878151260504201,
            "Final Electricity Consumption by Process (kWh/year)": 150000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 540000.0,
            "Total Primary Energy Consumption (MJ/year)": 1770491.8032786886
        },
        "Grinding": {
            "Production Per Process (tonnes/year)": 270000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 3240000.0,
            "% Electricity Consumption at production stage": 0.17016806722689076,
            "Final Electricity Consumption by Process (kWh/year)": 3240000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 11664000.0,
            "Total Primary Energy Consumption (MJ/year)": 38242622.95081967
        },
        "Additive prepration": {
            "Production Per Process (tonnes/year)": 120000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 1000000.0,
            "% Electricity Consumption at production stage": 0.052521008403361345,
            "Final Electricity Consumption by Process (kWh/year)": 1000000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 3600000.0,
            "Total Primary Energy Consumption (MJ/year)": 11803278.68852459
        },
        "Additive drying": {
            "Production Per Process (tonnes/year)": 10000.0,
            "fuel": {
                "coal": 15000000.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 0.0,
            "% Electricity Consumption at production stage": 0.0,
            "Final Electricity Consumption by Process (kWh/year)": 0.0,
            "Final Fuel Consumption by Process (MJ/year)": 15000000.0,
            "Total Final Energy Consumption (MJ/year)": 15000000.0,
            "Total Primary Energy Consumption (MJ/year)": 15000000.0
        },
        "Fuel preparation": {
            "Production Per Process (tonnes/year)": 16301.777777777776,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 450000.0,
            "% Electricity Consumption at production stage": 0.023634453781512604,
            "Final Electricity Consumption by Process (kWh/year)": 450000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 1620000.0,
            "Total Primary Energy Consumption (MJ/year)": 5311475.409836066
        },
        "Homogenization": {
            "Production Per Process (tonnes/year)": 270000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 400000.0,
            "% Electricity Consumption at production stage": 0.02100840336134454,
            "Final Electricity Consumption by Process (kWh/year)": 400000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 1440000.0,
            "Total Primary Energy Consumption (MJ/year)": 4721311.4754098365
        },
        "Kiln system - preheater": {
            "Production Per Process (tonnes/year)": 100000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 1000000.0,
            "% Electricity Consumption at production stage": 0.052521008403361345,
            "Final Electricity Consumption by Process (kWh/year)": 1000000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 3600000.0,
            "Total Primary Energy Consumption (MJ/year)": 11803278.68852459
        },
        "Kiln system - precalciner": {
            "Production Per Process (tonnes/year)": 100000.0,
            "fuel": {
                "coal": 15000000.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 0.0,
            "% Electricity Consumption at production stage": 0.0,
            "Final Electricity Consumption by Process (kWh/year)": 0.0,
            "Final Fuel Consumption by Process (MJ/year)": 15000000.0,
            "Total Final Energy Consumption (MJ/year)": 15000000.0,
            "Total Primary Energy Consumption (MJ/year)": 15000000.0
        },
        "Kiln system - kiln": {
            "Production Per Process (tonnes/year)": 100000.0,
            "fuel": {
                "coal": 390000000.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 0.0,
            "% Electricity Consumption at production stage": 0.0,
            "Final Electricity Consumption by Process (kWh/year)": 0.0,
            "Final Fuel Consumption by Process (MJ/year)": 390000000.0,
            "Total Final Energy Consumption (MJ/year)": 390000000.0,
            "Total Primary Energy Consumption (MJ/year)": 390000000.0
        },
        "Kiln system - cooler": {
            "Production Per Process (tonnes/year)": 100000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 4500000.0,
            "% Electricity Consumption at production stage": 0.23634453781512604,
            "Final Electricity Consumption by Process (kWh/year)": 4500000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 16200000.0,
            "Total Primary Energy Consumption (MJ/year)": 53114754.09836066
        },
        "Cement grinding": {
            "Production Per Process (tonnes/year)": 125000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 6500000.0,
            "% Electricity Consumption at production stage": 0.34138655462184875,
            "Final Electricity Consumption by Process (kWh/year)": 6500000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 23400000.0,
            "Total Primary Energy Consumption (MJ/year)": 76721311.47540984
        },
        "Other conveying, auxilaries": {
            "Production Per Process (tonnes/year)": 125000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 1250000.0,
            "% Electricity Consumption at production stage": 0.06565126050420168,
            "Final Electricity Consumption by Process (kWh/year)": 1250000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 4500000.0,
            "Total Primary Energy Consumption (MJ/year)": 14754098.360655738
        },
        "Non-production energy use": {
            "Production Per Process (tonnes/year)": 125000.0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 200000.0,
            "% Electricity Consumption at production stage": 0.01050420168067227,
            "Final Electricity Consumption by Process (kWh/year)": 200000.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 720000.0,
            "Total Primary Energy Consumption (MJ/year)": 2360655.7377049183
        },
        "Air pollution flue-gas mitigation": {
            "Production Per Process (tonnes/year)": 0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 0.0,
            "% Electricity Consumption at production stage": 0.0,
            "Final Electricity Consumption by Process (kWh/year)": 0.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 0.0,
            "Total Primary Energy Consumption (MJ/year)": 0.0
        },
        "CCUS": {
            "Production Per Process (tonnes/year)": 0,
            "fuel": {
                "coal": 0.0,
                "coke": 0.0,
                "natural gas": 0.0,
                "biomass": 0.0,
                "municipal wastes": 0.0
            },
            "electricity": 0.0,
            "% Electricity Consumption at production stage": 0.0,
            "Final Electricity Consumption by Process (kWh/year)": 0.0,
            "Final Fuel Consumption by Process (MJ/year)": 0.0,
            "Total Final Energy Consumption (MJ/year)": 0.0,
            "Total Primary Energy Consumption (MJ/year)": 0.0
        }
    },
    "Total Final Energy Consumption (MJ/year)": 488544000.0,
    "Total Primary Energy Consumption (MJ/year)": 644734426.2295082,
    "message": "N/A"
}
    
    if self.ui.ball_mill_raw_input.text() != "":
        energy_input_dict["Raw material grinding (%)"]["ball mill"] = _f(self.ui.ball_mill_raw_input.text())
    if self.ui.vert_roller_mill_raw_input.text() != "":
        energy_input_dict["Raw material grinding (%)"]["vertical roller mill"] = _f(self.ui.vert_roller_mill_raw_input.text())
    if self.ui.horizontal_roller_mill_raw_input.text() != "":
        energy_input_dict["Raw material grinding (%)"]["high pressure roller press/horizontal roller mill"] = _f(self.ui.horizontal_roller_mill_raw_input.text())

    if self.ui.vert_roller_mill_fuel_input.text() != "":
        energy_input_dict["Fuel grinding (%)"]["ball mill"] = _f(self.ui.vert_roller_mill_fuel_input.text())
    if self.ui.horizontal_roller_mill_fuel_input.text() != "":
        energy_input_dict["Fuel grinding (%)"]["vertical rolelr mill"] = _f(self.ui.horizontal_roller_mill_fuel_input.text())

    if self.ui.ball_mill_cement_input.text() != "":
        energy_input_dict["Cement grinding (%)"]["ball mill"] = _f(self.ui.ball_mill_cement_input.text())
    if self.ui.vert_roller_mill_cement_input.text() != "":
        energy_input_dict["Cement grinding (%)"]["vertical rolelr mill"] = _f(self.ui.vert_roller_mill_cement_input.text())
    if self.ui.horizontal_roller_mill_cement_input.text() != "":
        energy_input_dict["Cement grinding (%)"]["high pressure roller press/horizontal roller mill"] = _f(self.ui.horizontal_roller_mill_cement_input.text())


    with open(filepath, "w") as f:
        json.dump(energy_input_dict, f, indent=4)

    return energy_input_dict 

def Page6_Energy_Input_Quick_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)
    filepath = json_folder / "Energy_Input_Quick.json"
    energy_input_filepath = json_folder / "Energy_Input.json"

    with open(energy_input_filepath, "r") as f:
        energy_input_dict = json.load(f)

    energy_share_default_dict = {
    "Raw material conveying and quarraying": {
        "fuel": 0,
        "electricity": 0.02
    },
    "Preblending": {
        "fuel": 0,
        "electricity": 0.02
    },
    "Crushing": {
        "fuel": 0,
        "electricity": 0
    },
    "Grinding": {
        "fuel": 0,
        "electricity": 0.21
    },
    "Additive prepration": {
        "fuel": 0,
        "electricity": 0.01
    },
    "Additive drying": {
        "fuel": 0.03,
        "electricity": 0
    },
    "Fuel preparation": {
        "fuel": 0,
        "electricity": 0.03
    },
    "Homogenization": {
        "fuel": 0,
        "electricity": 0
    },
    "Kiln system - preheater": {
        "fuel": 0,
        "electricity": 0.22
    },
    "Kiln system - precalciner": {
        "fuel": 0,
        "electricity": 0
    },
    "Kiln system - kiln": {
        "fuel": 0.97,
        "electricity": 0
    },
    "Kiln system - cooler": {
        "fuel": 0,
        "electricity": 0
    },
    "Cement grinding": {
        "fuel": 0,
        "electricity": 0.42
    },
    "Other conveying, auxilaries": {
        "fuel": 0,
        "electricity": 0.06
    },
    "Non-production energy use": {
        "fuel": 0,
        "electricity": 0.01
    },
    "Air pollution flue-gas mitigation": {
        "fuel": 0,
        "electricity": 0
    },
    "CCUS": {
        "fuel": 0,
        "electricity": 0
    }}
    

    energy_input_quick_dict = {
    "Energy input": {
        "fuel": {
            "coal": 420000000.0,
            "coke": 0.0,
            "natural gas": 0.0,
            "biomass": 0.0,
            "municipal wastes": 0.0
        },
        "electricity": 19040000.0
    },
    "Total Final Energy Consumption (MJ/year)": 488544000.0,
    "Total Primary Energy Consumption (MJ/year)": 644734426.2295082,
    "message": "N/A"
}

    for process in energy_input_dict["Energy input"].keys():
        for fuel in energy_input_dict["Energy input"][process]["fuel"].keys():
            energy_input_dict["Energy input"][process]["fuel"][fuel] = energy_input_quick_dict["Energy input"]["fuel"][fuel] * energy_share_default_dict[process]["fuel"]
        energy_input_dict["Energy input"][process]["electricity"] = energy_input_quick_dict["Energy input"]["electricity"] * energy_share_default_dict[process]["electricity"]

    energy_input_quick_dict["Total Final Energy Consumption (MJ/year)"] = sum(energy_input_quick_dict["Energy input"]["fuel"].values()) + energy_input_quick_dict["Energy input"]["electricity"] * 3.6
    energy_input_quick_dict["Total Primary Energy Consumption (MJ/year)"] = sum(energy_input_quick_dict["Energy input"]["fuel"].values()) + energy_input_quick_dict["Energy input"]["electricity"] * 3.6 / 0.305


    # Energy Input
    ## Fuel and electricity consumption for each step
    Total_process_coal = 0
    Total_process_coke = 0
    Total_process_natural_gas = 0
    Total_process_biomass = 0
    Total_process_msw = 0
    Total_process_electricity = 0

    for process in energy_input_dict["Energy input"].keys():
        Total_process_coal += energy_input_dict["Energy input"][process]["fuel"]["coal"]
        Total_process_coke += energy_input_dict["Energy input"][process]["fuel"]["coke"]
        Total_process_natural_gas += energy_input_dict["Energy input"][process]["fuel"]["natural gas"]
        Total_process_biomass += energy_input_dict["Energy input"][process]["fuel"]["biomass"]
        Total_process_msw += energy_input_dict["Energy input"][process]["fuel"]["municipal wastes"]
        Total_process_electricity += energy_input_dict["Energy input"][process]["electricity"]

    # if Total_process_electricity != electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"] + electricity_generation_input_dict["Total electricity purchased (kWh/year)"]:
    #     print('total electricity consumption does not match')
    #     energy_input_dict["message"] = 'total electricity consumption does not match'
    # else:
    #     energy_input_dict["message"] = 'N/A'
    Total_process_fuel = Total_process_coal + Total_process_coke + Total_process_natural_gas + Total_process_biomass + Total_process_msw
    
    energy_input_dict["Totals"] = {
        "Total process fuel": Total_process_fuel,
        "Total process electricity": Total_process_electricity,
        "Total process coal": Total_process_coal,
        "Total process coke": Total_process_coke,
        "Total process natural gas": Total_process_natural_gas,
        "Total process biomass": Total_process_biomass,
        "Total process msw": Total_process_msw
    }

    # Cost and Emissions Data
    with open(json_folder / "Cost_and_Emission_Input.json", "r") as f:
        cost_and_emissions_dict = json.load(f)

    electricity_price = cost_and_emissions_dict["Cost of electricity in $/kWh"]
    coal_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['coal']
    coke_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['coke']
    natural_gas_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['natural gas']
    biomass_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['biomass']
    msw_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['municipal wastes']

    electricity_emission_intensity = cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000 # convert to kWh # need to add emissions from electricity generation fuel, so do it later # decided to use this variable only for purchased electricity to aid indirect emissions calculations
    coal_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coal']/10**6 # convert to MJ
    coke_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coke']/10**6
    natural_gas_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['natural gas']/10**6 
    biomass_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['biomass']/10**6 
    msw_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['municipal wastes']/10**6 
    carbon_price = cost_and_emissions_dict["Carbon price ($/tCO2)"]

    fuel_price = (Total_process_coal*coal_price + Total_process_coke*coke_price + Total_process_natural_gas*natural_gas_price + Total_process_biomass*biomass_price + Total_process_msw*msw_price) / Total_process_fuel
    fuel_emission_intensity = (Total_process_coal*coal_emission_intensity + Total_process_coke*coke_emission_intensity + Total_process_natural_gas*natural_gas_emission_intensity + Total_process_biomass*biomass_emission_intensity + Total_process_msw*msw_emission_intensity) / Total_process_fuel

    cost_and_emissions_dict["Fuel Emission Intensity"] = fuel_emission_intensity
    cost_and_emissions_dict["Fuel Price"] = fuel_price
    # Save the updated dictionary
    with open(json_folder / "Cost_and_Emission_Input.json", "w") as f:
        json.dump(cost_and_emissions_dict, f, indent=4)

    # Electricity Generation Data
    with open(json_folder / "Electricity_Generation_Input.json", "r") as f:
        electricity_generation_input_dict = json.load(f)

    Total_coal_with_generation_and_process = Total_process_coal + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coal"]
    Total_coal_with_generation_and_process_in_mass = Total_coal_with_generation_and_process * 0.00003412/0.9 # convert MJ of coal into tce, and then 0.9 tce is 1 tonne of coal

    Total_coke_with_generation_and_process = Total_process_coke + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coke"]
    Total_natural_gas_with_generation_and_process = Total_process_natural_gas + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["natural gas"]
    Total_biomass_with_generation_and_process = Total_process_biomass + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["biomass"]
    Total_msw_with_generation_and_process = Total_process_msw + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["municipal wastes"]

    #Production Data
    with open(json_folder / "Production_Input.json", "r") as f:
        production_input_dict = json.load(f)

    Total_raw_material_and_additive = production_input_dict["Amount of limestone used per year (tonnes/year)"] + production_input_dict["Amount of gypsum used per year (tonnes/year)"] + production_input_dict["Amount of calcined clay used per year (tonnes/year)"] + production_input_dict["Amount of blast furnace slag used per year (tonnes/year)"] + production_input_dict["Amount of other slag used per year (tonnes/year)"] + production_input_dict["Amount of fly ash used per year (tonnes/year)"] + production_input_dict["Amount of other natural pozzolans used per year (tonnes/year)"]
    Total_clinker = production_input_dict["Total clinker production"]
    Total_cement = production_input_dict["Total cement"]

    ## Production volume for each step
    energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of limestone used per year (tonnes/year)"]
    energy_input_dict["Energy input"]["Preblending"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of raw materials preblended"]
    energy_input_dict["Energy input"]["Crushing"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of raw materials crushed"]
    energy_input_dict["Energy input"]["Grinding"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of raw materials crushed"]
    energy_input_dict["Energy input"]["Additive prepration"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of additives ground"]
    energy_input_dict["Energy input"]["Additive drying"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of additives dried"]
    energy_input_dict["Energy input"]["Fuel preparation"]["Production Per Process (tonnes/year)"] = Total_coal_with_generation_and_process_in_mass
    energy_input_dict["Energy input"]["Homogenization"]["Production Per Process (tonnes/year)"] = Total_raw_material_and_additive
    energy_input_dict["Energy input"]["Kiln system - preheater"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Kiln system - precalciner"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Kiln system - kiln"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Kiln system - cooler"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Cement grinding"]["Production Per Process (tonnes/year)"] = Total_cement
    energy_input_dict["Energy input"]["Other conveying, auxilaries"]["Production Per Process (tonnes/year)"] = Total_cement
    energy_input_dict["Energy input"]["Non-production energy use"]["Production Per Process (tonnes/year)"] = Total_cement

    for process in energy_input_dict["Energy input"].keys():
        energy_input_dict["Energy input"][process]["% Electricity Consumption at production stage"] = energy_input_dict["Energy input"][process]["electricity"] / Total_process_electricity
        energy_input_dict["Energy input"][process]["Final Electricity Consumption by Process (kWh/year)"] = energy_input_dict["Energy input"][process]["electricity"]
        energy_input_dict["Energy input"][process]["Final Fuel Consumption by Process (MJ/year)"] = sum(energy_input_dict["Energy input"][process]["fuel"].values())
        energy_input_dict["Energy input"][process]["Total Final Energy Consumption (MJ/year)"] = energy_input_dict["Energy input"][process]["Final Electricity Consumption by Process (kWh/year)"]*3.6 + energy_input_dict["Energy input"][process]["Final Fuel Consumption by Process (MJ/year)"]
        energy_input_dict["Energy input"][process]["Total Primary Energy Consumption (MJ/year)"] = energy_input_dict["Energy input"][process]["Final Electricity Consumption by Process (kWh/year)"]*3.6/0.305 + energy_input_dict["Energy input"][process]["Final Fuel Consumption by Process (MJ/year)"]

    Total_final_energy = 0
    Total_primary_energy = 0

    for process in energy_input_dict["Energy input"].keys():
        Total_final_energy += energy_input_dict["Energy input"][process]["Total Final Energy Consumption (MJ/year)"]
        Total_primary_energy += energy_input_dict["Energy input"][process]["Total Primary Energy Consumption (MJ/year)"]
    # Note: (ignore this comment, the latest version is that it is not included) for primary energy, no need to add back the fuel used for electricity generation, because that is already included when process electricity is calculated. The same conversion efficiency is assumed for converting electricity's primary energy consumption for both onsite and offsite generation 
    # Note: in this iteration, for primary energy from electriciuty, we treat the primary energy from final electricity the same whether they are generated onsite or purchased

    energy_input_dict["Total Final Energy Consumption (MJ/year)"] = Total_final_energy
    energy_input_dict["Total Primary Energy Consumption (MJ/year)"] = Total_primary_energy
    energy_input_dict["Total Process Fuel Consumption"] = Total_process_fuel

    with open(json_folder / "Electricity_Generation.json", "w") as f:
        json.dump(electricity_generation_input_dict, f, indent=4)

    print("energy_input_dict end of Page 6")
    print(energy_input_dict["Totals"].keys())

    with open(filepath, "w") as f:
        json.dump(energy_input_quick_dict, f, indent=4)

    with open(energy_input_filepath, "w") as f:
        json.dump(energy_input_dict, f, indent=4)

    with open(json_folder / "Energy_Share_Default.json", "w") as f:
        json.dump(energy_share_default_dict, f, indent=4)

    return energy_input_quick_dict 

def Page6_Energy_Input_Detailed_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)

    energy_input_filepath = json_folder / "Energy_Input.json"

    with open(energy_input_filepath, "r") as f:
        energy_input_dict = json.load(f)

    if self.ui.biomass_additive_dry_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive drying"]["fuel"]["biomass"] = _f(self.ui.biomass_additive_dry_input_page6.text())
    if self.ui.biomass_additive_prep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive prepration"]["fuel"]["biomass"] = _f(self.ui.biomass_additive_prep_input_page6.text())
    if self.ui.biomass_conveying_input_page6.text() != "":
        energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["fuel"]["biomass"] = _f(self.ui.biomass_conveying_input_page6.text())
    if self.ui.biomass_crushing_input_page6.text() != "":
        energy_input_dict["Energy input"]["Crushing"]["fuel"]["biomass"] = _f(self.ui.biomass_crushing_input_page6.text())
    if self.ui.biomass_fuelprep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Fuel preparation"]["fuel"]["biomass"] = _f(self.ui.biomass_fuelprep_input_page6.text())
    if self.ui.biomass_grinding_input_page6_2.text() != "":
        energy_input_dict["Energy input"]["Grinding"]["fuel"]["biomass"] = _f(self.ui.biomass_grinding_input_page6_2.text())
    if self.ui.biomass_homo_input_page6.text() != "":
        energy_input_dict["Energy input"]["Homogenization"]["fuel"]["biomass"] = _f(self.ui.biomass_homo_input_page6.text())
    if self.ui.biomass_kiln_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - preheater"]["fuel"]["biomass"] = _f(self.ui.biomass_kiln_input_page6.text())
    if self.ui.biomass_preblending_input_page6.text() != "":
        energy_input_dict["Energy input"]["Preblending"]["fuel"]["biomass"] = _f(self.ui.biomass_preblending_input_page6.text())
    if self.ui.biomass_kiln_precalciner_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - precalciner"]["fuel"]["biomass"] = _f(self.ui.biomass_kiln_precalciner_input_page6.text())


    if self.ui.coal_additive_dry_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive drying"]["fuel"]["coal"] = _f(self.ui.coal_additive_dry_input_page6.text())
    if self.ui.coal_additive_prep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive prepration"]["fuel"]["coal"] = _f(self.ui.coal_additive_prep_input_page6.text())
    if self.ui.coal_conveying_input_page6.text() != "":
        energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["fuel"]["coal"] = _f(self.ui.coal_conveying_input_page6.text())
    if self.ui.coal_crushing_input_page6.text() != "":
        energy_input_dict["Energy input"]["Crushing"]["fuel"]["coal"] = _f(self.ui.coal_crushing_input_page6.text())
    if self.ui.coal_fuelprep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Fuel preparation"]["fuel"]["coal"] = _f(self.ui.coal_fuelprep_input_page6.text())
    if self.ui.coal_grinding_input_page6_2.text() != "":
        energy_input_dict["Energy input"]["Grinding"]["fuel"]["coal"] = _f(self.ui.coal_grinding_input_page6_2.text())
    if self.ui.coal_homo_input_page6.text() != "":
        energy_input_dict["Energy input"]["Homogenization"]["fuel"]["coal"] = _f(self.ui.coal_homo_input_page6.text())
    if self.ui.coal_kiln_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - preheater"]["fuel"]["coal"] = _f(self.ui.coal_kiln_input_page6.text())
    if self.ui.coal_preblending_input_page6.text() != "":
        energy_input_dict["Energy input"]["Preblending"]["fuel"]["coal"] = _f(self.ui.coal_preblending_input_page6.text())
    if self.ui.coal_kiln_precalciner_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - precalciner"]["fuel"]["coal"] = _f(self.ui.coal_kiln_precalciner_input_page6.text())
    if self.ui.coke_additive_dry_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive drying"]["fuel"]["coke"] = _f(self.ui.coke_additive_dry_input_page6.text())
    if self.ui.coke_additive_prep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive prepration"]["fuel"]["coke"] = _f(self.ui.coke_additive_prep_input_page6.text())
    if self.ui.coke_conveying_input_page6.text() != "":
        energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["fuel"]["coke"] = _f(self.ui.coke_conveying_input_page6.text())
    if self.ui.coke_crushing_input_page6.text() != "":
        energy_input_dict["Energy input"]["Crushing"]["fuel"]["coke"] = _f(self.ui.coke_crushing_input_page6.text())
    if self.ui.coke_fuelprep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Fuel preparation"]["fuel"]["coke"] = _f(self.ui.coke_fuelprep_input_page6.text())
    if self.ui.coke_grinding_input_page6_2.text() != "":
        energy_input_dict["Energy input"]["Grinding"]["fuel"]["coke"] = _f(self.ui.coke_grinding_input_page6_2.text())
    if self.ui.coke_homo_input_page6.text() != "":  
        energy_input_dict["Energy input"]["Homogenization"]["fuel"]["coke"] = _f(self.ui.coke_homo_input_page6.text())
    if self.ui.coke_kiln_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - preheater"]["fuel"]["coke"] = _f(self.ui.coke_kiln_input_page6.text())
    if self.ui.coke_preblending_input_page6.text() != "":
        energy_input_dict["Energy input"]["Preblending"]["fuel"]["coke"] = _f(self.ui.coke_preblending_input_page6.text())
    if self.ui.coke_kiln_precalciner_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - precalciner"]["fuel"]["coke"] = _f(self.ui.coke_kiln_precalciner_input_page6.text())
    if self.ui.electricity_additive_dry_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive drying"]["electricity"] = _f(self.ui.electricity_additive_dry_input_page6.text())
    if self.ui.electricity_additive_prep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive prepration"]["electricity"] = _f(self.ui.electricity_additive_prep_input_page6.text())
    if self.ui.electricity_conveying_input_page6.text() != "":
        energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["electricity"] = _f(self.ui.electricity_conveying_input_page6.text())
    if self.ui.electricity_crushing_input_page6.text() != "":
        energy_input_dict["Energy input"]["Crushing"]["electricity"] = _f(self.ui.electricity_crushing_input_page6.text())
    if self.ui.electricity_fuelprep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Fuel preparation"]["electricity"] = _f(self.ui.electricity_fuelprep_input_page6.text())
    if self.ui.electricity_grinding_input_page6_2.text() != "":
        energy_input_dict["Energy input"]["Grinding"]["electricity"] = _f(self.ui.electricity_grinding_input_page6_2.text())
    if self.ui.electricity_homo_input_page6.text() != "":
        energy_input_dict["Energy input"]["Homogenization"]["electricity"] = _f(self.ui.electricity_homo_input_page6.text())
    if self.ui.electricity_kiln_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - preheater"]["electricity"] = _f(self.ui.electricity_kiln_input_page6.text())
    if self.ui.electricity_preblending_input_page6.text() != "":
        energy_input_dict["Energy input"]["Preblending"]["electricity"] = _f(self.ui.electricity_preblending_input_page6.text())
    if self.ui.electricity_kiln_precalciner_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - precalciner"]["electricity"] = _f(self.ui.electricity_kiln_precalciner_input_page6.text())
    if self.ui.msw_additive_dry_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive drying"]["fuel"]["municipal wastes"] = _f(self.ui.msw_additive_dry_input_page6.text())
    if self.ui.msw_additive_prep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive prepration"]["fuel"]["municipal wastes"] = _f(self.ui.msw_additive_prep_input_page6.text())
    if self.ui.msw_conveying_input_page6.text() != "":
        energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["fuel"]["municipal wastes"] = _f(self.ui.msw_conveying_input_page6.text())
    if self.ui.msw_crushing_input_page6.text() != "":
        energy_input_dict["Energy input"]["Crushing"]["fuel"]["municipal wastes"] = _f(self.ui.msw_crushing_input_page6.text())
    if self.ui.msw_fuelprep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Fuel preparation"]["fuel"]["municipal wastes"] = _f(self.ui.msw_fuelprep_input_page6.text())
    if self.ui.msw_grinding_input_page6_2.text() != "":
        energy_input_dict["Energy input"]["Grinding"]["fuel"]["municipal wastes"] = _f(self.ui.msw_grinding_input_page6_2.text())
    if self.ui.msw_homo_input_page6.text() != "":
        energy_input_dict["Energy input"]["Homogenization"]["fuel"]["municipal wastes"] = _f(self.ui.msw_homo_input_page6.text())
    if self.ui.msw_kiln_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - preheater"]["fuel"]["municipal wastes"] = _f(self.ui.msw_kiln_input_page6.text())
    if self.ui.msw_preblending_input_page6.text() != "":
        energy_input_dict["Energy input"]["Preblending"]["fuel"]["municipal wastes"] = _f(self.ui.msw_preblending_input_page6.text())
    if self.ui.msw_kiln_precalciner_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - precalciner"]["fuel"]["municipal wastes"] = _f(self.ui.msw_kiln_precalciner_input_page6.text())
    if self.ui.natural_gas_additive_dry_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive drying"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_additive_dry_input_page6.text())
    if self.ui.natural_gas_additive_prep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Additive prepration"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_additive_prep_input_page6.text())
    if self.ui.natural_gas_conveying_input_page6.text() != "":
        energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_conveying_input_page6.text())
    if self.ui.natural_gas_crushing_input_page6.text() != "":
        energy_input_dict["Energy input"]["Crushing"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_crushing_input_page6.text())
    if self.ui.natural_gas_fuelprep_input_page6.text() != "":
        energy_input_dict["Energy input"]["Fuel preparation"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_fuelprep_input_page6.text())
    if self.ui.natural_gas_grinding_input_page6_2.text() != "":
        energy_input_dict["Energy input"]["Grinding"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_grinding_input_page6_2.text())
    if self.ui.natural_gas_homo_input_page6.text() != "":
        energy_input_dict["Energy input"]["Homogenization"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_homo_input_page6.text())
    if self.ui.natural_gas_kiln_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - preheater"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_kiln_input_page6.text())
    if self.ui.natural_gas_preblending_input_page6.text() != "":
        energy_input_dict["Energy input"]["Preblending"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_preblending_input_page6.text())
    if self.ui.natural_gas_kiln_precalciner_input_page6.text() != "":
        energy_input_dict["Energy input"]["Kiln system - precalciner"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_kiln_precalciner_input_page6.text())


    with open(energy_input_filepath, "w") as f:
        json.dump(energy_input_dict, f, indent=4)

def Page6_Energy_Input_Detailed_Default_Update_Fields_2(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)

    energy_input_filepath = json_folder / "Energy_Input.json"

    with open(energy_input_filepath, "r") as f:
        energy_input_dict = json.load(f)

    if self.ui.coal_kiln_kiln_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - kiln"]["fuel"]["coal"] = _f(self.ui.coal_kiln_kiln_page6_b.text())
    if self.ui.coal_kiln_cooler_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - cooler"]["fuel"]["coal"] = _f(self.ui.coal_kiln_cooler_page6_b.text())
    if self.ui.coal_cement_grinding_page6_b.text() != "":
        energy_input_dict["Energy input"]["Cement grinding"]["fuel"]["coal"] = _f(self.ui.coal_cement_grinding_page6_b.text())
    if self.ui.coal_other_conveying_page6_b.text() != "":
        energy_input_dict["Energy input"]["Other conveying, auxilaries"]["fuel"]["coal"] = _f(self.ui.coal_other_conveying_page6_b.text())
    if self.ui.coal_non_production_page6_b.text() != "":
        energy_input_dict["Energy input"]["Non-production energy use"]["fuel"]["coal"] = _f(self.ui.coal_non_production_page6_b.text())
    if self.ui.coal_air_pollution_page6_b.text() != "":
        energy_input_dict["Energy input"]["Air pollution flue-gas mitigation"]["fuel"]["coal"] = _f(self.ui.coal_air_pollution_page6_b.text())
    if self.ui.coal_ccus_page6_b.text() != "":
        energy_input_dict["Energy input"]["CCUS"]["fuel"]["coal"] = _f(self.ui.coal_ccus_page6_b.text())

    if self.ui.coke_kiln_kiln_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - kiln"]["fuel"]["coke"] = _f(self.ui.coke_kiln_kiln_page6_b.text())
    if self.ui.coke_kiln_cooler_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - cooler"]["fuel"]["coke"] = _f(self.ui.coke_kiln_cooler_page6_b.text())
    if self.ui.coke_cement_grinding_page6_b.text() != "":
        energy_input_dict["Energy input"]["Cement grinding"]["fuel"]["coke"] = _f(self.ui.coke_cement_grinding_page6_b.text())
    if self.ui.coke_other_conveying_page6_b.text() != "":
        energy_input_dict["Energy input"]["Other conveying, auxilaries"]["fuel"]["coke"] = _f(self.ui.coke_other_conveying_page6_b.text())
    if self.ui.coke_non_production_page6_b.text() != "":
        energy_input_dict["Energy input"]["Non-production energy use"]["fuel"]["coke"] = _f(self.ui.coke_non_production_page6_b.text())
    if self.ui.coke_air_pollution_page6_b.text() != "":
        energy_input_dict["Energy input"]["Air pollution flue-gas mitigation"]["fuel"]["coke"] = _f(self.ui.coke_air_pollution_page6_b.text())
    if self.ui.coke_ccus_page6_b.text() != "":
        energy_input_dict["Energy input"]["CCUS"]["fuel"]["coke"] = _f(self.ui.coke_ccus_page6_b.text())

    if self.ui.natural_gas_kiln_kiln_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - kiln"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_kiln_kiln_page6_b.text())
    if self.ui.natural_gas_kiln_cooler_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - cooler"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_kiln_cooler_page6_b.text())
    if self.ui.natural_gas_cement_grinding_page6_b.text() != "":
        energy_input_dict["Energy input"]["Cement grinding"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_cement_grinding_page6_b.text())
    if self.ui.natural_gas_other_conveying_page6_b.text() != "":
        energy_input_dict["Energy input"]["Other conveying, auxilaries"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_other_conveying_page6_b.text())
    if self.ui.natural_gas_non_production_page6_b.text() != "":
        energy_input_dict["Energy input"]["Non-production energy use"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_non_production_page6_b.text())
    if self.ui.natural_gas_air_pollution_page6_b.text() != "":
        energy_input_dict["Energy input"]["Air pollution flue-gas mitigation"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_air_pollution_page6_b.text())
    if self.ui.natural_gas_ccus_page6_b.text() != "":
        energy_input_dict["Energy input"]["CCUS"]["fuel"]["natural gas"] = _f(self.ui.natural_gas_ccus_page6_b.text())
        
    if self.ui.biomass_kiln_kiln_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - kiln"]["fuel"]["biomass"] = _f(self.ui.biomass_kiln_kiln_page6_b.text())
    if self.ui.biomass_kiln_cooler_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - cooler"]["fuel"]["biomass"] = _f(self.ui.biomass_kiln_cooler_page6_b.text())
    if self.ui.biomass_cement_grinding_page6_b.text() != "":
        energy_input_dict["Energy input"]["Cement grinding"]["fuel"]["biomass"] = _f(self.ui.biomass_cement_grinding_page6_b.text())
    if self.ui.biomass_other_conveying_page6_b.text() != "":
        energy_input_dict["Energy input"]["Other conveying, auxilaries"]["fuel"]["biomass"] = _f(self.ui.biomass_other_conveying_page6_b.text())
    if self.ui.biomass_non_production_page6_b.text() != "":
        energy_input_dict["Energy input"]["Non-production energy use"]["fuel"]["biomass"] = _f(self.ui.biomass_non_production_page6_b.text())
    if self.ui.biomass_air_pollution_page6_b.text() != "":
        energy_input_dict["Energy input"]["Air pollution flue-gas mitigation"]["fuel"]["biomass"] = _f(self.ui.biomass_air_pollution_page6_b.text())
    if self.ui.biomass_ccus_page6_b.text() != "":
        energy_input_dict["Energy input"]["CCUS"]["fuel"]["biomass"] = _f(self.ui.biomass_ccus_page6_b.text())
        
    if self.ui.msw_kiln_kiln_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - kiln"]["fuel"]["municipal wastes"] = _f(self.ui.msw_kiln_kiln_page6_b.text())
    if self.ui.msw_kiln_cooler_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - cooler"]["fuel"]["municipal wastes"] = _f(self.ui.msw_kiln_cooler_page6_b.text())
    if self.ui.msw_cement_grinding_page6_b.text() != "":
        energy_input_dict["Energy input"]["Cement grinding"]["fuel"]["municipal wastes"] = _f(self.ui.msw_cement_grinding_page6_b.text())
    if self.ui.msw_other_conveying_page6_b.text() != "":
        energy_input_dict["Energy input"]["Other conveying, auxilaries"]["fuel"]["municipal wastes"] = _f(self.ui.msw_other_conveying_page6_b.text())
    if self.ui.msw_non_production_page6_b.text() != "":
        energy_input_dict["Energy input"]["Non-production energy use"]["fuel"]["municipal wastes"] = _f(self.ui.msw_non_production_page6_b.text())
    if self.ui.msw_air_pollution_page6_b.text() != "":
        energy_input_dict["Energy input"]["Air pollution flue-gas mitigation"]["fuel"]["municipal wastes"] = _f(self.ui.msw_air_pollution_page6_b.text())
    if self.ui.msw_ccus_page6_b.text() != "":
        energy_input_dict["Energy input"]["CCUS"]["fuel"]["municipal wastes"] = _f(self.ui.msw_ccus_page6_b.text())
        
    if self.ui.electricity_kiln_kiln_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - kiln"]["electricity"] = _f(self.ui.electricity_kiln_kiln_page6_b.text())
    if self.ui.electricity_kiln_cooler_page6_b.text() != "":
        energy_input_dict["Energy input"]["Kiln system - cooler"]["electricity"] = _f(self.ui.electricity_kiln_cooler_page6_b.text())
    if self.ui.electricity_cement_grinding_page6_b.text() != "":
        energy_input_dict["Energy input"]["Cement grinding"]["electricity"] = _f(self.ui.electricity_cement_grinding_page6_b.text())
    if self.ui.electricity_other_conveying_page6_b.text() != "":
        energy_input_dict["Energy input"]["Other conveying, auxilaries"]["electricity"] = _f(self.ui.electricity_other_conveying_page6_b.text())
    if self.ui.electricity_non_production_page6_b.text() != "":
        energy_input_dict["Energy input"]["Non-production energy use"]["electricity"] = _f(self.ui.electricity_non_production_page6_b.text())
    if self.ui.electricity_air_pollution_page6_b.text() != "":
        energy_input_dict["Energy input"]["Air pollution flue-gas mitigation"]["electricity"] = _f(self.ui.electricity_air_pollution_page6_b.text())
    if self.ui.electricity_ccus_page6_b.text() != "":
        energy_input_dict["Energy input"]["CCUS"]["electricity"] = _f(self.ui.electricity_ccus_page6_b.text())
        
    # Energy Input
    ## Fuel and electricity consumption for each step
    Total_process_coal = 0
    Total_process_coke = 0
    Total_process_natural_gas = 0
    Total_process_biomass = 0
    Total_process_msw = 0
    Total_process_electricity = 0

    for process in energy_input_dict["Energy input"].keys():
        Total_process_coal += energy_input_dict["Energy input"][process]["fuel"]["coal"]
        Total_process_coke += energy_input_dict["Energy input"][process]["fuel"]["coke"]
        Total_process_natural_gas += energy_input_dict["Energy input"][process]["fuel"]["natural gas"]
        Total_process_biomass += energy_input_dict["Energy input"][process]["fuel"]["biomass"]
        Total_process_msw += energy_input_dict["Energy input"][process]["fuel"]["municipal wastes"]
        Total_process_electricity += energy_input_dict["Energy input"][process]["electricity"]

    # if Total_process_electricity != electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"] + electricity_generation_input_dict["Total electricity purchased (kWh/year)"]:
    #     print('total electricity consumption does not match')
    #     energy_input_dict["message"] = 'total electricity consumption does not match'
    # else:
    #     energy_input_dict["message"] = 'N/A'
    Total_process_fuel = Total_process_coal + Total_process_coke + Total_process_natural_gas + Total_process_biomass + Total_process_msw
    
    energy_input_dict["Totals"] = {
        "Total process fuel": Total_process_fuel,
        "Total process electricity": Total_process_electricity,
        "Total process coal": Total_process_coal,
        "Total process coke": Total_process_coke,
        "Total process natural gas": Total_process_natural_gas,
        "Total process biomass": Total_process_biomass,
        "Total process msw": Total_process_msw
    }

    # Cost and Emissions Data
    with open(json_folder / "Cost_and_Emission_Input.json", "r") as f:
        cost_and_emissions_dict = json.load(f)

    electricity_price = cost_and_emissions_dict["Cost of electricity in $/kWh"]
    coal_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['coal']
    coke_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['coke']
    natural_gas_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['natural gas']
    biomass_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['biomass']
    msw_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['municipal wastes']

    electricity_emission_intensity = cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000 # convert to kWh # need to add emissions from electricity generation fuel, so do it later # decided to use this variable only for purchased electricity to aid indirect emissions calculations
    coal_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coal']/10**6 # convert to MJ
    coke_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coke']/10**6
    natural_gas_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['natural gas']/10**6 
    biomass_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['biomass']/10**6 
    msw_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['municipal wastes']/10**6 
    carbon_price = cost_and_emissions_dict["Carbon price ($/tCO2)"]

    fuel_price = (Total_process_coal*coal_price + Total_process_coke*coke_price + Total_process_natural_gas*natural_gas_price + Total_process_biomass*biomass_price + Total_process_msw*msw_price) / Total_process_fuel
    fuel_emission_intensity = (Total_process_coal*coal_emission_intensity + Total_process_coke*coke_emission_intensity + Total_process_natural_gas*natural_gas_emission_intensity + Total_process_biomass*biomass_emission_intensity + Total_process_msw*msw_emission_intensity) / Total_process_fuel

    cost_and_emissions_dict["Fuel Emission Intensity"] = fuel_emission_intensity
    cost_and_emissions_dict["Fuel Price"] = fuel_price
    # Save the updated dictionary
    with open(json_folder / "Cost_and_Emission_Input.json", "w") as f:
        json.dump(cost_and_emissions_dict, f, indent=4)

    # Electricity Generation Data
    with open(json_folder / "Electricity_Generation_Input.json", "r") as f:
        electricity_generation_input_dict = json.load(f)

    Total_coal_with_generation_and_process = Total_process_coal + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coal"]
    Total_coal_with_generation_and_process_in_mass = Total_coal_with_generation_and_process * 0.00003412/0.9 # convert MJ of coal into tce, and then 0.9 tce is 1 tonne of coal

    Total_coke_with_generation_and_process = Total_process_coke + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coke"]
    Total_natural_gas_with_generation_and_process = Total_process_natural_gas + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["natural gas"]
    Total_biomass_with_generation_and_process = Total_process_biomass + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["biomass"]
    Total_msw_with_generation_and_process = Total_process_msw + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["municipal wastes"]

    #Production Data
    with open(json_folder / "Production_Input.json", "r") as f:
        production_input_dict = json.load(f)

    Total_raw_material_and_additive = production_input_dict["Amount of limestone used per year (tonnes/year)"] + production_input_dict["Amount of gypsum used per year (tonnes/year)"] + production_input_dict["Amount of calcined clay used per year (tonnes/year)"] + production_input_dict["Amount of blast furnace slag used per year (tonnes/year)"] + production_input_dict["Amount of other slag used per year (tonnes/year)"] + production_input_dict["Amount of fly ash used per year (tonnes/year)"] + production_input_dict["Amount of other natural pozzolans used per year (tonnes/year)"]
    Total_clinker = production_input_dict["Total clinker production"]
    Total_cement = production_input_dict["Total cement"]

    ## Production volume for each step
    energy_input_dict["Energy input"]["Raw material conveying and quarraying"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of limestone used per year (tonnes/year)"]
    energy_input_dict["Energy input"]["Preblending"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of raw materials preblended"]
    energy_input_dict["Energy input"]["Crushing"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of raw materials crushed"]
    energy_input_dict["Energy input"]["Grinding"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of raw materials crushed"]
    energy_input_dict["Energy input"]["Additive prepration"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of additives ground"]
    energy_input_dict["Energy input"]["Additive drying"]["Production Per Process (tonnes/year)"] = production_input_dict["Amount of additives dried"]
    energy_input_dict["Energy input"]["Fuel preparation"]["Production Per Process (tonnes/year)"] = Total_coal_with_generation_and_process_in_mass
    energy_input_dict["Energy input"]["Homogenization"]["Production Per Process (tonnes/year)"] = Total_raw_material_and_additive
    energy_input_dict["Energy input"]["Kiln system - preheater"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Kiln system - precalciner"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Kiln system - kiln"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Kiln system - cooler"]["Production Per Process (tonnes/year)"] = Total_clinker
    energy_input_dict["Energy input"]["Cement grinding"]["Production Per Process (tonnes/year)"] = Total_cement
    energy_input_dict["Energy input"]["Other conveying, auxilaries"]["Production Per Process (tonnes/year)"] = Total_cement
    energy_input_dict["Energy input"]["Non-production energy use"]["Production Per Process (tonnes/year)"] = Total_cement

    for process in energy_input_dict["Energy input"].keys():
        energy_input_dict["Energy input"][process]["% Electricity Consumption at production stage"] = energy_input_dict["Energy input"][process]["electricity"] / Total_process_electricity
        energy_input_dict["Energy input"][process]["Final Electricity Consumption by Process (kWh/year)"] = energy_input_dict["Energy input"][process]["electricity"]
        energy_input_dict["Energy input"][process]["Final Fuel Consumption by Process (MJ/year)"] = sum(energy_input_dict["Energy input"][process]["fuel"].values())
        energy_input_dict["Energy input"][process]["Total Final Energy Consumption (MJ/year)"] = energy_input_dict["Energy input"][process]["Final Electricity Consumption by Process (kWh/year)"]*3.6 + energy_input_dict["Energy input"][process]["Final Fuel Consumption by Process (MJ/year)"]
        energy_input_dict["Energy input"][process]["Total Primary Energy Consumption (MJ/year)"] = energy_input_dict["Energy input"][process]["Final Electricity Consumption by Process (kWh/year)"]*3.6/0.305 + energy_input_dict["Energy input"][process]["Final Fuel Consumption by Process (MJ/year)"]

    Total_final_energy = 0
    Total_primary_energy = 0

    for process in energy_input_dict["Energy input"].keys():
        Total_final_energy += energy_input_dict["Energy input"][process]["Total Final Energy Consumption (MJ/year)"]
        Total_primary_energy += energy_input_dict["Energy input"][process]["Total Primary Energy Consumption (MJ/year)"]
    # Note: (ignore this comment, the latest version is that it is not included) for primary energy, no need to add back the fuel used for electricity generation, because that is already included when process electricity is calculated. The same conversion efficiency is assumed for converting electricity's primary energy consumption for both onsite and offsite generation 
    # Note: in this iteration, for primary energy from electriciuty, we treat the primary energy from final electricity the same whether they are generated onsite or purchased


    energy_input_dict["Total Final Energy Consumption (MJ/year)"] = Total_final_energy
    energy_input_dict["Total Primary Energy Consumption (MJ/year)"] = Total_primary_energy
    energy_input_dict["Total Process Fuel Consumption"] = Total_process_fuel

    with open(json_folder / "Electricity_Generation.json", "w") as f:
        json.dump(electricity_generation_input_dict, f, indent=4)

    with open(json_folder / "Energy_Input.json", "w") as f:
        json.dump(energy_input_dict, f, indent=4)


    print("energy_input_dict end of Page 6")
    print(energy_input_dict["Totals"].keys())

    return energy_input_dict 

def Page7_Target_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    # Energy Billing Input
    energy_billing_input_dict = {
    "name": "Energy Billing Input",
    "Energy Billing Data (USD/year)": {
        "coal": 14333333.333333334,
        "coke": 0.0,
        "natural gas": 0.0,
        "biomass": 0.0,
        "municipal wastes": 0.0,
        "purchased electricity": 952000,
        "electricity": 3608000.0
    },
    "Total (USD/year)": 18893333.333333336,
    "Total Energy Bill (USD/year) - [user entered, for reference only]": 0.0}

    # Energy Billing Input Data
    with open(json_folder / "Energy_Billing_Input.json", "w") as f:
        json.dump(energy_billing_input_dict, f, indent=4)

    # Energy Input Data
    with open(json_folder / "Energy_Input.json", "r") as f:
        energy_input_dict = json.load(f)

    print("energy_input_dict start of Page 7")
    print(energy_input_dict["Totals"].keys())

    Total_process_electricity = energy_input_dict["Totals"]["Total process electricity"]
    Total_process_coal = energy_input_dict["Totals"]["Total process coal"]
    Total_process_coke = energy_input_dict["Totals"]["Total process coke"]
    Total_process_natural_gas = energy_input_dict["Totals"]["Total process natural gas"]
    Total_process_biomass = energy_input_dict["Totals"]["Total process biomass"]
    Total_process_msw = energy_input_dict["Totals"]["Total process msw"]

    # Electricity Generation Data
    with open(json_folder / "Electricity_Generation.json", "r") as f:
        electricity_generation_input_dict = json.load(f)

    # Cost and Emissions Data
    with open(json_folder / "Cost_and_Emission_Input.json", "r") as f:
        cost_and_emissions_dict = json.load(f)

    electricity_price = cost_and_emissions_dict["Cost of electricity in $/kWh"]
    coal_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['coal']
    coke_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['coke']
    natural_gas_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['natural gas']
    biomass_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['biomass']
    msw_price = cost_and_emissions_dict["Cost of fuel in $/MJ"]['municipal wastes']

    Total_coal_with_generation_and_process = Total_process_coal + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coal"]
    Total_coal_with_generation_and_process_in_mass = Total_coal_with_generation_and_process * 0.00003412/0.9 # convert MJ of coal into tce, and then 0.9 tce is 1 tonne of coal

    Total_coke_with_generation_and_process = Total_process_coke + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["coke"]
    Total_natural_gas_with_generation_and_process = Total_process_natural_gas + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["natural gas"]
    Total_biomass_with_generation_and_process = Total_process_biomass + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["biomass"]
    Total_msw_with_generation_and_process = Total_process_msw + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"]["municipal wastes"]
    
    energy_billing_input_dict["Energy Billing Data (USD/year)"]["electricity"] = (Total_process_electricity-electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"])*electricity_price # electricity_generation_input_dict["Total electricity purchased (kWh/year)"]*electricity_price # use the calculated value in case purchased electricity is entered wrong
    energy_billing_input_dict["Energy Billing Data (USD/year)"]["electricity"] = (Total_process_electricity-electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"])*electricity_price # electricity_generation_input_dict["Total electricity purchased (kWh/year)"]*electricity_price # use the calculated value in case purchased electricity is entered wrong

    energy_billing_input_dict["Energy Billing Data (USD/year)"]["coal"] = Total_coal_with_generation_and_process*coal_price
    energy_billing_input_dict["Energy Billing Data (USD/year)"]["coke"] = Total_coke_with_generation_and_process*coke_price
    energy_billing_input_dict["Energy Billing Data (USD/year)"]["natural gas"] = Total_natural_gas_with_generation_and_process*natural_gas_price
    energy_billing_input_dict["Energy Billing Data (USD/year)"]["biomass"] = Total_biomass_with_generation_and_process*biomass_price
    energy_billing_input_dict["Energy Billing Data (USD/year)"]["municipal wastes"] = Total_msw_with_generation_and_process*msw_price

    energy_billing_input_dict["Total (USD/year)"] = sum(energy_billing_input_dict["Energy Billing Data (USD/year)"].values())

    target_dict = {
    "name": "Target",
    "Annual energy use (GJ)": 488544.0,
    "Energy percentage reduction": 20.0,
    "Absolute (final energy) reduction": 97708.8,
    "Annual direct CO2 emissions before CCUS (million metric ton CO2)": {
        "coal": 0.00093,
        "coke": 0.0,
        "natural gas": 0.0
    },
    "Total annual direct CO2 emissions before CCUS (million metric ton CO2)": 0.00093,
    "Annual direct CO2 emissions with CCUS (million metric ton CO2)": 0.00093,
    "Annual indirect CO2 emissions (million metric ton CO2)": 0.00902,
    "Annual CO2 emissions (million metric ton CO2)": 0.00995,
    "Direct CO2 emissions percentage reduction": 20.0,
    "Indirect CO2 emissions percentage reduction": 20.0,
    "Overall (including process) CO2 emissions percentage reduction": 20.0,
    "Absolute CO2 emissions reduction (million metric ton CO2)": 0.199}

    if self.ui.energy_percent_reduction_input.text() != "":
        target_dict["Energy percentage reduction"] = _f(self.ui.energy_percent_reduction_input.text())
    if self.ui.direct_percent_reduction_input.text() != "":
        target_dict["Direct CO2 emissions percentage reduction"] = _f(self.ui.direct_percent_reduction_input.text())
    if self.ui.indirect_percent_reduction_input.text() != "":
        target_dict["Indirect CO2 emissions percentage reduction"] = _f(self.ui.indirect_percent_reduction_input.text())
    if self.ui.overall_percent_reduction_input.text() != "":
        target_dict["Overall (including process) CO2 emissions percentage reduction"] = _f(self.ui.overall_percent_reduction_input.text())

    # Energy Input Data
    with open(json_folder / "Energy_Input.json", "r") as f:
        energy_input_dict = json.load(f)

    Total_final_energy = energy_input_dict["Total Final Energy Consumption (MJ/year)"]
    
    target_dict["Annual energy use (GJ)"] = Total_final_energy/1000
    target_dict["Absolute (final energy) reduction"] = target_dict["Annual energy use (GJ)"] * target_dict["Energy percentage reduction"]/100 # need to /100 if the results are expressed in % values

    for fuel in target_dict["Annual direct CO2 emissions before CCUS (million metric ton CO2)"].keys():
        for process in energy_input_dict["Energy input"].keys(): # added this for clarity 
            target_dict["Annual direct CO2 emissions before CCUS (million metric ton CO2)"][fuel] = (energy_input_dict["Energy input"][process]["fuel"][fuel] + electricity_generation_input_dict["Energy used for electricity generation (MJ/year)"][fuel])*(cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"][fuel]/10**6)/10**6

    purchased_electricity = Total_process_electricity - electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"]

    # Carbon Capture Data
    with open(json_folder / "Carbon_Capture_Input.json", "r") as f:
        carbon_capture_dict = json.load(f)

    target_dict["Total annual direct CO2 emissions before CCUS (million metric ton CO2)"] = sum(target_dict["Annual direct CO2 emissions before CCUS (million metric ton CO2)"].values())
    target_dict["Annual direct CO2 emissions with CCUS (million metric ton CO2)"] = target_dict["Total annual direct CO2 emissions before CCUS (million metric ton CO2)"] - carbon_capture_dict["CO2 captured (million metric tons/year)"]
    target_dict["Annual indirect CO2 emissions (million metric ton CO2)"] = purchased_electricity *(cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000)/10**6
    target_dict["Annual CO2 emissions (million metric ton CO2)"] = target_dict["Annual direct CO2 emissions with CCUS (million metric ton CO2)"] + target_dict["Annual indirect CO2 emissions (million metric ton CO2)"]
    target_dict["Absolute CO2 emissions reduction (million metric ton CO2)"] = target_dict["Annual CO2 emissions (million metric ton CO2)"]*target_dict["Overall (including process) CO2 emissions percentage reduction"] # need to /100 if the results are expressed in % values

    Target_final = Total_final_energy * (100-target_dict["Energy percentage reduction"])/100
    target_dict["Target Final"] = Target_final
    target_dict["Purchased Electricity"] = purchased_electricity
    
    # Save the updated dictionary
    with open(json_folder / "Target_Input.json", "w") as f:
        json.dump(target_dict, f, indent=4)

    return target_dict

# Detailed Output
def Part_1_Detailed_Output(self):
    data_dir = get_user_data_dir()
    json_folder = data_dir / "Saved Progress"
    json_folder.mkdir(parents=True, exist_ok=True)


    detailed_output_dict = {
    "name": "Detailed Output",
    "Preblending": {
        "Your Facility": 350000.0,
        "International Best Practice Facility": 270000.0,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Crushing": {
        "Your Facility": 150000.0,
        "International Best Practice Facility": 102600.0,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Grinding": {
        "Your Facility": 3240000.0,
        "International Best Practice Facility": 3091500.0,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Homogenization": {
        "Your Facility": 400000.0,
        "International Best Practice Facility": 27000.0,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Fuel preparation": {
        "name": "Fuel grinding and preparation",
        "Your Facility": 450000.0,
        "International Best Practice Facility": 163017.77777777775,
        "National Best Practice Facility": 0,
        "category": "Fuel Preparation",
        "unit": "kWh/year"
    },
    "Additive prepration": {
        "name": "Additive grinding and blending",
        "Your Facility": 1000000.0,
        "International Best Practice Facility": 2400000.0,
        "National Best Practice Facility": 0,
        "category": "Additives Preparation",
        "unit": "kWh/year"
    },
    "Additive drying": {
        "Your Facility": 15000000.0,
        "International Best Practice Facility": 7500000.0,
        "National Best Practice Facility": 0,
        "category": "Additives Preparation",
        "unit": "MJ/year"
    },
    "Kiln system - preheater": {
        "Your Facility": 1000000.0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Machinery Use",
        "unit": "kWh/year"
    },
    "Kiln system - cooler": {
        "name": "Kiln system - clinker cooler",
        "Your Facility": 4500000.0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Machinery Use",
        "unit": "kWh/year"
    },
    "Total kiln mechanical electricity": {
        "Your Facility": 5500000.0,
        "International Best Practice Facility": 2250000.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Machinery Use",
        "unit": "kWh/year"
    },
    "Kiln system - precalciner": {
        "Your Facility": 15000000.0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Clinker Making",
        "unit": "MJ/year"
    },
    "Kiln system - kiln": {
        "Your Facility": 390000000.0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Clinker Making",
        "unit": "MJ/year"
    },
    "Total for clinker making fuel": {
        "Your Facility": 405000000.0,
        "International Best Practice Facility": 285000000.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Clinker Making",
        "unit": "MJ/year"
    },
    "Pure Portland cement": {
        "Your Facility": 0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "N/A"
    },
    "Common Portland cement": {
        "Your Facility": 0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "N/A"
    },
    "Slag cement": {
        "Your Facility": 0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "N/A"
    },
    "Fly ash cement": {
        "Your Facility": 0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "N/A"
    },
    "Pozzolana cement": {
        "Your Facility": 0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "N/A"
    },
    "Blended limestone cement": {
        "Your Facility": 0,
        "International Best Practice Facility": 0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "N/A"
    },
    "Cement grinding": {
        "name": "Total finish grinding energy",
        "Your Facility": 6500000.0,
        "International Best Practice Facility": 4550000.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Raw material conveying and quarraying": {
        "name": "Quarrying",
        "Your Facility": 0.0,
        "International Best Practice Facility": 190400.0,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Auxiliaries": {
        "Your Facility": 1250000.0,
        "International Best Practice Facility": 1000000.0,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Conveyors": {
        "Your Facility": float("nan"),
        "International Best Practice Facility": 187500.0,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Total Electricity - Production - other": {
        "Your Facility": 1250000.0,
        "International Best Practice Facility": 1377900.0,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Non-production energy use": {
        "name": "Total Electricity - Non-production - other",
        "Your Facility": 200000.0,
        "International Best Practice Facility": 228480.0,
        "National Best Practice Facility": 0,
        "category": "Other-Non-production Energy",
        "unit": "kWh/year"
    }
}

    # Save the detailed output dictionary
    with open(json_folder / "Detailed_Output.json", 'w') as f:
        json.dump(detailed_output_dict, f, indent=4)

    international_best_practice_dict = {
    "name": "International Best Practice",
    "Preblending": {
        "Value": 1,
        "Energy unit": "kWh/t",
        "Quantity": "raw material"
    },
    "Crushing": {
        "Value": 0.38,
        "Energy unit": "kWh/t",
        "Quantity": "raw material"
    },
    "Grinding": {
        "Value": 11.45,
        "Energy unit": "kWh/t",
        "Quantity": "raw material with mill distribution"
    },
    "Grinding Detailed": {
        "Value": {
		"ball mill": 11.45,
		"vertical roller mill": 11.45,
		"high pressure roller press/horizontal roller mill": 11.45
	},
        "Energy unit": "kWh/t",
        "Quantity": "raw material with mill distribution"
    },	
    "Homogenization": {
        "Value": 0.1,
        "Energy unit": "kWh/t",
        "Quantity": "raw material"
    },
    "Fuel preparation": {
        "Value": 10,
        "Energy unit": "kWh/t",
        "Quantity": "coal"
    },
    "Additive prepration": {
        "Value": 20,
        "Energy unit": "kWh/t",
        "Quantity": "additive grinding"
    },
    "Additive drying": {
        "Value": 750,
        "Energy unit": "MJ/t",
        "Quantity": "additive drying"
    },
    "Total kiln mechanical electricity": {
        "Value": 22.5,
        "Energy unit": "kWh/t",
        "Quantity": "clinker"
    },
    "Total for clinker making fuel": {
        "Value": 2850,
        "Energy unit": "MJ/t",
        "Quantity": "clinker"
    },
    "Total finish grinding energy": {
        "Value": {
            "Pure Portland cement": 19.2,
            "Common Portland cement": 17.3,
            "Slag cement": 44,
            "Fly ash cement": 25,
            "Pozzolana cement": 44,
            "Blended cement": 19
        },
        "Energy unit": "kWh/t",
        "Quantity": "cement by type"
    },
    "Raw material conveying and quarraying": {
        "Value": 0.01,
        "Energy unit": "share of facility electricity",
        "Quantity": "N/A"
    },
    "Auxiliaries": {
        "Value": 10,
        "Energy unit": "kWh/t",
        "Quantity": "clinker"
    },
    "Conveyors": {
        "Value": 1.5,
        "Energy unit": "kWh/t",
        "Quantity": "cement"
    },
    "Non-production energy use": {
        "Value": 0.012,
        "Energy unit": "share of facility electricity",
        "Quantity": "N/A"
    } }

    # Save the international best practice dictionary
    with open(json_folder / "International_Best_Practice.json", 'w') as f:
        json.dump(international_best_practice_dict, f, indent=4)

    # Energy Input Data
    with open(json_folder / "Energy_Input.json", "r") as f:
        energy_input_dict = json.load(f)

    for process in detailed_output_dict.keys():
        try: 
            if detailed_output_dict[process]["unit"] == "kWh/year":
                detailed_output_dict[process]["Your Facility"] = energy_input_dict["Energy input"][process]["Final Electricity Consumption by Process (kWh/year)"]
            else:
                detailed_output_dict[process]["Your Facility"] = energy_input_dict["Energy input"][process]["Final Fuel Consumption by Process (MJ/year)"]
            detailed_output_dict[process]["International Best Practice Facility"] = energy_input_dict["Energy input"][process]["Production Per Process (tonnes/year)"] * international_best_practice_dict[process]["Value"]
        except:
            KeyError()

    ## Handle special cases
    dummy = 0
    for mill_type in international_best_practice_dict["Grinding Detailed"]["Value"].keys():
        dummy += energy_input_dict["Raw material grinding (%)"][mill_type]/100*international_best_practice_dict["Grinding Detailed"]["Value"][mill_type]*energy_input_dict["Energy input"]["Grinding"]["Production Per Process (tonnes/year)"] # /100 for converting percentage into share
    detailed_output_dict["Grinding"]["International Best Practice Facility"] = dummy

    cement_type_map = {
        "Pure Portland cement production (tonnes/year)": "Pure Portland cement",
        "Common Portland cement production (tonnes/year)": "Common Portland cement",
        "Slag cement production (tonnes/year)": "Slag cement",
        "Fly ash cement production (tonnes/year)": "Fly ash cement",
        "Pozzolana cement production (tonnes/year)": "Pozzolana cement",
        "Blended cement production (tonnes/year)": "Blended cement"
        }
    
    # Production Input Data
    with open(json_folder / "Production_Input.json", "r") as f:
        production_input_dict = json.load(f)

    Total_clinker = production_input_dict["Total clinker production"]
    Total_cement = production_input_dict["Total cement"]
    Total_process_electricity = energy_input_dict["Totals"]["Total process electricity"]

    dummy = 0
    for cement_type in production_input_dict["Cement production"].keys():
        dummy += production_input_dict["Cement production"][cement_type]*international_best_practice_dict["Total finish grinding energy"]["Value"][cement_type_map[cement_type]]
    detailed_output_dict["Cement grinding"]["International Best Practice Facility"] = dummy

    detailed_output_dict["Total kiln mechanical electricity"]["Your Facility"] = detailed_output_dict["Kiln system - preheater"]["Your Facility"] + detailed_output_dict["Kiln system - cooler"]["Your Facility"]
    detailed_output_dict["Total kiln mechanical electricity"]["International Best Practice Facility"] = Total_clinker * international_best_practice_dict["Total kiln mechanical electricity"]["Value"]
    detailed_output_dict["Total for clinker making fuel"]["Your Facility"] = detailed_output_dict["Kiln system - precalciner"]["Your Facility"] + detailed_output_dict["Kiln system - kiln"]["Your Facility"]
    detailed_output_dict["Total for clinker making fuel"]["International Best Practice Facility"] = Total_clinker * international_best_practice_dict["Total for clinker making fuel"]["Value"]
    #detailed_output_dict["Total finish grinding energy"]["International Best Practice Facility"] = "complicated"
    detailed_output_dict["Raw material conveying and quarraying"]["International Best Practice Facility"] = international_best_practice_dict["Raw material conveying and quarraying"]["Value"] * Total_process_electricity
    detailed_output_dict["Auxiliaries"]["Your Facility"] = energy_input_dict["Energy input"]["Other conveying, auxilaries"]["Final Electricity Consumption by Process (kWh/year)"]
    detailed_output_dict["Auxiliaries"]["International Best Practice Facility"] = Total_clinker * international_best_practice_dict["Auxiliaries"]["Value"]
    detailed_output_dict["Conveyors"]["Your Facility"] = np.nan # It's included in "Raw material conveying and quarraying" and "Auxiliaries"
    detailed_output_dict["Conveyors"]["International Best Practice Facility"] = Total_cement * international_best_practice_dict["Conveyors"]["Value"]
    detailed_output_dict["Non-production energy use"]["International Best Practice Facility"] = international_best_practice_dict["Non-production energy use"]["Value"] * Total_process_electricity

    IBP_total_electricity = 0
    IBP_total_fuel = 0

    list_of_processes = list(detailed_output_dict.keys())
    list_of_processes.remove('name')

    for process in list_of_processes:
        if detailed_output_dict[process]["unit"] == "kWh/year":
            IBP_total_electricity += detailed_output_dict[process]["International Best Practice Facility"] # be careful of double counting values from the grouped categories
        elif detailed_output_dict[process]["unit"] == "MJ/year":
            IBP_total_fuel += detailed_output_dict[process]["International Best Practice Facility"]

    IBP_total_final_energy = IBP_total_electricity*3.6 + IBP_total_fuel
    IBP_total_primary_energy = IBP_total_electricity*3.6/0.305 + IBP_total_fuel

    detailed_output_dict["IBP total final energy"] = IBP_total_final_energy
    detailed_output_dict["IBP total primary energy"] = IBP_total_primary_energy
    detailed_output_dict["IBP total fuel"] = IBP_total_fuel
    detailed_output_dict["IBP total electricity"] = IBP_total_electricity

    detailed_output_dict["Total Electricity - Production - other"]["Your Facility"] = detailed_output_dict["Raw material conveying and quarraying"]["Your Facility"] + detailed_output_dict["Auxiliaries"]["Your Facility"] # place here to prevent double counting for the IBP calculations
    detailed_output_dict["Total Electricity - Production - other"]["International Best Practice Facility"] = detailed_output_dict["Raw material conveying and quarraying"]["International Best Practice Facility"] + detailed_output_dict["Auxiliaries"]["International Best Practice Facility"] + detailed_output_dict["Conveyors"]["International Best Practice Facility"]

    # Detailed_Output_Emissions
    detailed_output_emissions_dict = {
    "name": "Detailed Output Emissions",
    "Preblending": {
        "Your Facility": 175.0,
        "International Best Practice Facility": 135.0,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Crushing": {
        "Your Facility": 75.0,
        "International Best Practice Facility": 51.3,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Grinding": {
        "Your Facility": 1620.0,
        "International Best Practice Facility": 1545.75,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Homogenization": {
        "Your Facility": 200.0,
        "International Best Practice Facility": 13.5,
        "National Best Practice Facility": 0,
        "category": "Raw Materials Preparation",
        "unit": "kWh/year"
    },
    "Fuel preparation": {
        "name": "Fuel grinding and preparation",
        "Your Facility": 225.0,
        "International Best Practice Facility": 81.50888888888888,
        "National Best Practice Facility": 0,
        "category": "Fuel Preparation",
        "unit": "kWh/year"
    },
    "Additive prepration": {
        "name": "Additive grinding and blending",
        "Your Facility": 500.0,
        "International Best Practice Facility": 1200.0,
        "National Best Practice Facility": 0,
        "category": "Additives Preparation",
        "unit": "kWh/year"
    },
    "Additive drying": {
        "Your Facility": 1395.0,
        "International Best Practice Facility": 697.5,
        "National Best Practice Facility": 0,
        "category": "Additives Preparation",
        "unit": "MJ/year"
    },
    "Kiln system - preheater": {
        "Your Facility": 500.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Machinery Use",
        "unit": "kWh/year"
    },
    "Kiln system - cooler": {
        "name": "Kiln system - clinker cooler",
        "Your Facility": 2250.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Machinery Use",
        "unit": "kWh/year"
    },
    "Total kiln mechanical electricity": {
        "Your Facility": 2750.0,
        "International Best Practice Facility": 1125.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Machinery Use",
        "unit": "kWh/year"
    },
    "Kiln system - precalciners": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Clinker Making",
        "unit": "MJ/year"
    },
    "Kiln system  - kiln": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Clinker Making",
        "unit": "MJ/year"
    },
    "Total for clinker making fuel": {
        "Your Facility": 37665.0,
        "International Best Practice Facility": 26505.0,
        "National Best Practice Facility": 0,
        "category": "Kiln - Clinker Making",
        "unit": "MJ/year"
    },
    "Pure Portland cement": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Common Portland cement": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Slag cement": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Fly ash cement": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Pozzolana cement": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Blended limestone cement": {
        "Your Facility": 0.0,
        "International Best Practice Facility": 0.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Cement grinding": {
        "name": "Total finish grinding energy",
        "Your Facility": 3250.0,
        "International Best Practice Facility": 2275.0,
        "National Best Practice Facility": 0,
        "category": "Cement Grinding - Finished Product",
        "unit": "kWh/year"
    },
    "Raw material conveying and quarraying": {
        "name": "Quarrying",
        "Your Facility": 0.0,
        "International Best Practice Facility": 95.2,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Auxiliaries": {
        "Your Facility": 625.0,
        "International Best Practice Facility": 500.0,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Conveyors": {
        "Your Facility": 0,
        "International Best Practice Facility": 93.75,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Total Electricity - Production - other": {
        "Your Facility": 625.0,
        "International Best Practice Facility": 688.95,
        "National Best Practice Facility": 0,
        "category": "Other-Production Energy",
        "unit": "kWh/year"
    },
    "Non-production energy use": {
        "name": "Total Electricity - Non-production - other",
        "Your Facility": 100.0,
        "International Best Practice Facility": 114.24,
        "National Best Practice Facility": 0,
        "category": "Other-Non-production Energy",
        "unit": "kWh/year"
    }
}

    # Cost_and_Emissions Data
    with open(json_folder / "Cost_and_Emission_Input.json", "r") as f:
        cost_and_emissions_dict = json.load(f)

    fuel_emission_intensity = cost_and_emissions_dict["Fuel Emission Intensity"]

    for process in detailed_output_dict.keys():
        try: 
            if detailed_output_dict[process]["unit"] == "kWh/year":
                detailed_output_emissions_dict[process]["Your Facility"] = detailed_output_dict[process]["Your Facility"] * cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000
                detailed_output_emissions_dict[process]["International Best Practice Facility"] = detailed_output_dict[process]["International Best Practice Facility"] * cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000
            else:
                detailed_output_emissions_dict[process]["Your Facility"] = detailed_output_dict[process]["Your Facility"] * fuel_emission_intensity # shifted away from using coal to using an average fuel emission intensity
                detailed_output_emissions_dict[process]["International Best Practice Facility"] = detailed_output_dict[process]["International Best Practice Facility"] * fuel_emission_intensity # shifted away from using coal to using an average fuel emission intensity
                
        except:
            KeyError()
    
    with open(json_folder / "Detailed_Output_Emissions.json", 'w') as f:
        json.dump(detailed_output_emissions_dict, f, indent=4)

    # Benchmarking_Results_Primary
    benchmarking_results_primary_dict = {
        "name": "Benchmarking Results Primary",
        "International Benchmarking": {
        "Primary Energy Intensity Index": 134.4751525965144,
        "Electricity Consumption (kWh/year)": {
            "Your Facility": 19040000.0,
            "International Best Practice Facility": 15838397.777777778,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0.0
        },
        "Comprehensive Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 152.32,
            "International Best Practice Facility": 126.70718222222223,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Purchased Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 144.32,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Fuel Consumption (MJ/year)": {
            "Your Facility": 420000000.0,
            "International Best Practice Facility": 292500000.0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0.0
        },
        "Comprehensive Fuel Intensity (MJ/tonne clinker)": {
            "Your Facility": 3360.0,
            "International Best Practice Facility": 2340.0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final (site) Energy Consumption (MJ/year)": {
            "Your Facility": 488544000.0,
            "International Best Practice Facility": 349518232.0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0.0
        },
        "Final (site) Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 3908.352,
            "International Best Practice Facility": 2796.145856,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Consumption (MJ/year)": {
            "Your Facility": 644734426.2295082,
            "International Best Practice Facility": 479445022.9508197,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 5157.875409836065,
            "International Best Practice Facility": 3835.5601836065575,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final Energy Intensity Index": 139.77639941827127
        },
        "Domestic Benchmarking": {
        "Primary Energy Intensity Index": 0,
        "Electricity Consumption (kWh/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Comprehensive Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Purchased Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Fuel Consumption (MJ/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Comprehensive Fuel Intensity (MJ/tonne clinker)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final (site) Energy Consumption (MJ/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final (site) Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Consumption (MJ/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        }
            }}
    
    # #Energy Input Data
    Total_primary_energy = energy_input_dict["Total Primary Energy Consumption (MJ/year)"]
    Total_final_energy = energy_input_dict["Total Final Energy Consumption (MJ/year)"]
    Total_process_fuel = energy_input_dict["Totals"]["Total process fuel"]

    # Production Input Data
    with open(json_folder / "Production_Input.json", "r") as f:
        production_input_dict = json.load(f)
    Total_cement = production_input_dict["Total cement"]
    print("total cement is:", Total_cement)

    # Electricity Generation Input Data
    with open(json_folder / "Electricity_Generation_Input.json", "r") as f:
        electricity_generation_input_dict = json.load(f)

    # Benchmarking Results Primary
    benchmarking_results_primary_dict["International Benchmarking"]["Primary Energy Intensity Index"] = 100*Total_primary_energy/IBP_total_primary_energy
    benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"]["Your Facility"] = Total_process_electricity
    benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"]["International Best Practice Facility"] = IBP_total_electricity
    benchmarking_results_primary_dict["International Benchmarking"]["Comprehensive Electricity Intensity (kWh/tonne cement)"]["Your Facility"] = Total_process_electricity / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Comprehensive Electricity Intensity (kWh/tonne cement)"]["International Best Practice Facility"] = IBP_total_electricity / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Purchased Electricity Intensity (kWh/tonne cement)"]["Your Facility"] = (Total_process_electricity - electricity_generation_input_dict["Electricity generated and used at cement plant (kWh/year)"]) / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"]["Your Facility"] = Total_process_fuel
    benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"]["International Best Practice Facility"] = IBP_total_fuel
    benchmarking_results_primary_dict["International Benchmarking"]["Comprehensive Fuel Intensity (MJ/tonne clinker)"]["Your Facility"] = Total_process_fuel / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Comprehensive Fuel Intensity (MJ/tonne clinker)"]["International Best Practice Facility"] = IBP_total_fuel / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Final (site) Energy Consumption (MJ/year)"]["Your Facility"] = Total_final_energy
    benchmarking_results_primary_dict["International Benchmarking"]["Final (site) Energy Consumption (MJ/year)"]["International Best Practice Facility"] = IBP_total_final_energy
    benchmarking_results_primary_dict["International Benchmarking"]["Final (site) Energy Intensity (MJ/tonne cement produced)"]["Your Facility"] = Total_final_energy / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Final (site) Energy Intensity (MJ/tonne cement produced)"]["International Best Practice Facility"] = IBP_total_final_energy / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Primary Energy Consumption (MJ/year)"]["Your Facility"] = Total_primary_energy
    benchmarking_results_primary_dict["International Benchmarking"]["Primary Energy Consumption (MJ/year)"]["International Best Practice Facility"] = IBP_total_primary_energy
    benchmarking_results_primary_dict["International Benchmarking"]["Primary Energy Intensity (MJ/tonne cement produced)"]["Your Facility"] = Total_primary_energy / Total_cement
    benchmarking_results_primary_dict["International Benchmarking"]["Primary Energy Intensity (MJ/tonne cement produced)"]["International Best Practice Facility"] = IBP_total_primary_energy / Total_cement

    for metric in benchmarking_results_primary_dict["International Benchmarking"].keys():
        try:
            benchmarking_results_primary_dict["International Benchmarking"][metric]["Potential for Efficiency Improvement"] = benchmarking_results_primary_dict["International Benchmarking"][metric]["Your Facility"] - benchmarking_results_primary_dict["International Benchmarking"][metric]["Primary Energy Intensity (MJ/tonne cement produced)"]
        except:
            KeyError()
            
    benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"]["Potential Cost Reduction (USD/year)"] = benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"]["Potential for Efficiency Improvement"] * cost_and_emissions_dict["Cost of electricity in $/kWh"]
    benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"]["Potential Cost Reduction (USD/year)"] = benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"]["Potential for Efficiency Improvement"] * cost_and_emissions_dict["Cost of fuel in $/MJ"]["coal"]
    benchmarking_results_primary_dict["International Benchmarking"]["Final (site) Energy Consumption (MJ/year)"]["Potential Cost Reduction (USD/year)"] = benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"]["Potential Cost Reduction (USD/year)"] + benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"]["Potential Cost Reduction (USD/year)"]

    with open(json_folder / "Benchmarking_Results_Primary.json", 'w') as f:
        json.dump(benchmarking_results_primary_dict, f, indent=4)

    # Benchmarking Results Final
    benchmarking_results_final_dict = {
    "name": "Benchmarking Results Primary",
    "International Benchmarking": {
        "Primary Energy Intensity Index": 134.4751525965144,
        "Electricity Consumption (kWh/year)": {
            "Your Facility": 19040000.0,
            "International Best Practice Facility": 15838397.777777778,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0.0
        },
        "Comprehensive Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 152.32,
            "International Best Practice Facility": 126.70718222222223,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Purchased Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 144.32,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Fuel Consumption (MJ/year)": {
            "Your Facility": 420000000.0,
            "International Best Practice Facility": 292500000.0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0.0
        },
        "Comprehensive Fuel Intensity (MJ/tonne clinker)": {
            "Your Facility": 3360.0,
            "International Best Practice Facility": 2340.0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final (site) Energy Consumption (MJ/year)": {
            "Your Facility": 488544000.0,
            "International Best Practice Facility": 349518232.0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0.0
        },
        "Final (site) Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 3908.352,
            "International Best Practice Facility": 2796.145856,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Consumption (MJ/year)": {
            "Your Facility": 644734426.2295082,
            "International Best Practice Facility": 479445022.9508197,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 5157.875409836065,
            "International Best Practice Facility": 3835.5601836065575,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final Energy Intensity Index": 139.77639941827127
    },
    "Domestic Benchmarking": {
        "Primary Energy Intensity Index": 0,
        "Electricity Consumption (kWh/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Comprehensive Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Purchased Electricity Intensity (kWh/tonne cement)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Fuel Consumption (MJ/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Comprehensive Fuel Intensity (MJ/tonne clinker)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final (site) Energy Consumption (MJ/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Final (site) Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Consumption (MJ/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        },
        "Primary Energy Intensity (MJ/tonne cement produced)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for Efficiency Improvement": 0,
            "Potential Cost Reduction (USD/year)": 0
        }
    }
}
    
    benchmarking_results_final_dict = benchmarking_results_primary_dict

    benchmarking_results_final_dict["International Benchmarking"]["Final Energy Intensity Index"] = 100*Total_final_energy/IBP_total_final_energy

    with open(json_folder / "Benchmarking_Results_Final.json", 'w') as f:
        json.dump(benchmarking_results_final_dict, f, indent=4)

    # Target Data
    with open(json_folder / "Target_Input.json", "r") as f:
        target_dict = json.load(f)

    Target_final = target_dict["Target Final"]
    purchased_electricity = target_dict["Purchased Electricity"]

    # Plot graph
    fig, ax = plt.subplots(figsize=(7, 4))

    energy_use_comparison_labels = ['Your facility', 'Your target', 'National \n best practice', 'International \n best practice']
    energy_use_comparison_values = [Total_final_energy/10**6, Target_final/10**6, 0, IBP_total_final_energy/10**6] # convert from MJ to TJ
    bar_colors = ['black', 'grey', 'lime', 'green']

    ax.bar(energy_use_comparison_labels, energy_use_comparison_values, color=bar_colors)

    ax.set_ylabel('TJ/year')
    ax.set_title('Energy Use Comparisons (Final)')

    # Create a new directory for graphs
    graph_dir = data_dir / "Graphs"
    graph_dir.mkdir(parents=True, exist_ok=True)

    plt.savefig(graph_dir / "Energy Benchmark.png")
    plt.close()
    # plt.show()

    # Benchmarking Results CO2
    benchmarking_results_co2_dict = {
    "name": "Benchmarking Results CO2",
    "International Benchmarking": {
        "Indirect emission - energy (million tCO2/year)": {
            "Your Facility": 0.00952,
            "International Best Practice Facility": 0.007919198888888888,
            "Potential for CO2 Emission Reduction": 0.0,
            "Potential Carbon Cost Reduction (USD/year)": 0.0
        },
        "Direct emission - energy (million tCO2/year)": {
            "Your Facility": 0.03906,
            "International Best Practice Facility": 0.0272025,
            "Potential for CO2 Emission Reduction": 0.0,
            "Potential Carbon Cost Reduction (USD/year)": 0.0
        },
        "Direct emission - process (million tCO2/year)": {
            "Your Facility": 0,
            "International Best Practice Facility": 0,
            "Potential for CO2 Emission Reduction": 0,
            "Potential Carbon Cost Reduction (USD/year)": 0.0
        }
    } }

    co2_benchmark_parameters = ["Your Facility", "International Best Practice Facility", "Potential for CO2 Emission Reduction"]

    dummy_dict = {
        "Your Facility": "Your Facility",
        "International Best Practice Facility": "International Best Practice Facility",
        "Potential for CO2 Emission Reduction": "Potential for Efficiency Improvement"
        }
    
    electricity_emission_intensity = cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000 # convert to kWh # need to add emissions from electricity generation fuel, so do it later # decided to use this variable only for purchased electricity to aid indirect emissions calculations

    for parameter in co2_benchmark_parameters:
        benchmarking_results_co2_dict["International Benchmarking"]["Indirect emission - energy (million tCO2/year)"][parameter] = benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"][dummy_dict[parameter]] * electricity_emission_intensity/10**6
        benchmarking_results_co2_dict["International Benchmarking"]["Direct emission - energy (million tCO2/year)"][parameter] = benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"][dummy_dict[parameter]] * fuel_emission_intensity/10**6

    for item in benchmarking_results_co2_dict["International Benchmarking"].keys():
        benchmarking_results_co2_dict["International Benchmarking"][item]["Potential Carbon Cost Reduction (USD/year)"] = benchmarking_results_co2_dict["International Benchmarking"][item]["Potential for CO2 Emission Reduction"] * cost_and_emissions_dict["Carbon price ($/tCO2)"]

    with open(json_folder / "Electricity_Generation.json", "r") as f:
        electricity_generation_input_dict = json.load(f)

    electricity_generation_emissions =electricity_generation_input_dict["Electricity Generation Emissions"]
    onsite_RE_electricity_generation = electricity_generation_input_dict["Onsite Renewable Electricity Generation"]
    electricity_fuel_emission_intensity = electricity_generation_input_dict["Electricity Fuel Emission Intensity"]

    Total_carbon_indirect = purchased_electricity * cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000
    Total_carbon_direct = benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"]["Your Facility"] * fuel_emission_intensity + electricity_generation_emissions # may need to add emissions from electricity generation? (ignore following comment, it is already addressed) But this is already included in electricity emission intensity. Need to explore how to break this out 
    Total_process_carbon = Total_clinker*cost_and_emissions_dict["Process emission per metric ton of clinker (tCO2/t clinker)"]
    Total_carbon_all = Total_carbon_indirect + Total_carbon_direct + Total_process_carbon

    Target_carbon_indirect = Total_carbon_indirect * (100-target_dict["Indirect CO2 emissions percentage reduction"])/100
    Target_carbon_direct = Total_carbon_direct * (100-target_dict["Direct CO2 emissions percentage reduction"])/100
    Target_carbon_all = Total_carbon_all * (100-target_dict["Overall (including process) CO2 emissions percentage reduction"])/100

    benchmarking_results_primary_dict["Target carbon indirect"] = Target_carbon_indirect
    benchmarking_results_primary_dict["Target carbon direct"] = Target_carbon_direct
    benchmarking_results_primary_dict["Target carbon all"] = Target_carbon_all

    IBP_carbon_indirect = benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"]["International Best Practice Facility"] * cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000 * (purchased_electricity/Total_process_electricity) # for IBP, assume it uses the same share of purchased electricity
    IBP_carbon_direct = benchmarking_results_primary_dict["International Benchmarking"]["Fuel Consumption (MJ/year)"]["International Best Practice Facility"] * fuel_emission_intensity + benchmarking_results_primary_dict["International Benchmarking"]["Electricity Consumption (kWh/year)"]["International Best Practice Facility"]* (1 - ((purchased_electricity+onsite_RE_electricity_generation)/Total_process_electricity)) * (electricity_fuel_emission_intensity*3.6/0.305)
    IBP_carbon_all = IBP_carbon_indirect + IBP_carbon_direct + Total_clinker*cost_and_emissions_dict["Process emission per metric ton of clinker (tCO2/t clinker)"]

    benchmarking_results_primary_dict["IBP carbon indirect"] = IBP_carbon_indirect
    benchmarking_results_primary_dict["IBP carbon direct"] = IBP_carbon_direct
    benchmarking_results_primary_dict["IBP carbon all"] = IBP_carbon_all

    benchmarking_results_primary_dict["Total carbon direct"] = Total_carbon_direct
    benchmarking_results_primary_dict["Total carbon indirect"] = Total_carbon_indirect
    benchmarking_results_primary_dict["Total carbon all"] = Total_carbon_all
    benchmarking_results_primary_dict["Total process carbon"] = Total_process_carbon

    with open(json_folder / "Benchmarking_Results_CO2.json", 'w') as f:
        json.dump(benchmarking_results_co2_dict, f, indent=4)

    

    international_best_practice_intensity_values_dict = {
    "name": "International Best Practice Intensity Values",
    "Fuel emission intensity": 0.00004,
    "Clinker ratio": 0.5,
    "Overall emission intensity": 0}

    IBP_with_different_fuel_carbon_direct = IBP_carbon_direct * (international_best_practice_intensity_values_dict['Fuel emission intensity']/fuel_emission_intensity)
    #IBP_with_different_fuel_and_clinker_ratio_carbon_all = IBP_carbon_indirect + (IBP_with_different_fuel_carbon_direct + Total_clinker*cost_and_emissions_dict["Process emission per metric ton of clinker (tCO2/t clinker)"])*(international_best_practice_intensity_values_dict['Clinker ratio']/production_input_dict["Clinker to cement ratio"]) # this is only approximate, because not all direct energy is for clinker making
    IBP_with_different_fuel_and_process_carbon_all = Total_cement * international_best_practice_intensity_values_dict['Overall emission intensity']

    benchmarking_results_primary_dict["IBP with different fuel carbon direct"] = IBP_with_different_fuel_carbon_direct

    with open(json_folder / "Benchmarking_Results_Primary.json", 'w') as f:
        json.dump(benchmarking_results_primary_dict, f, indent=4)

    with open (json_folder / "International_Best_Practice_Intensity_Values.json", 'w') as f:
        json.dump(international_best_practice_dict,f, indent=4)


    # Plot graphs
    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)

    direct_carbon_comparison_labels = ['Your facility', 'Your target', 'National \n best practice', 'International \n best practice', 'International \n best practice \n with different fuel']
    direct_carbon_comparison_values = [Total_carbon_direct, Target_carbon_direct, 0, IBP_carbon_direct, IBP_with_different_fuel_carbon_direct]
    bar_colors = ['black', 'grey', 'lime', 'green', 'red']

    ax.bar(direct_carbon_comparison_labels, direct_carbon_comparison_values, color=bar_colors)

    ax.set_ylabel('tCO2/year')
    ax.set_title('Carbon Emissions Comparisons (Direct Energy)')

    plt.savefig(data_dir / "Graphs/Direct Energy CO2 Emissions Benchmark.png")
    plt.close()
    # plt.show()

    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)

    indirect_carbon_comparison_labels = ['Your facility', 'Your target', 'National \n best practice', 'International \n best practice']
    indirect_carbon_comparison_values = [Total_carbon_indirect, Target_carbon_indirect, 0, IBP_carbon_indirect]
    bar_colors = ['black', 'grey', 'lime', 'green']

    ax.bar(indirect_carbon_comparison_labels, indirect_carbon_comparison_values, color=bar_colors)

    ax.set_ylabel('tCO2/year')
    ax.set_title('Carbon Emissions Comparisons (indirect Energy)')

    plt.savefig(data_dir / "Graphs/Indirect Energy CO2 Emissions Benchmark.png")
    plt.close()
    # plt.show()

    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)

    all_carbon_comparison_labels = ['Your facility', 'Your target', 'National \n best practice', 'International \n best practice']
    all_carbon_comparison_values = [Total_carbon_all, Target_carbon_all, 0, IBP_carbon_all]
    bar_colors = ['black', 'grey', 'lime', 'green']

    ax.bar(all_carbon_comparison_labels, all_carbon_comparison_values, color=bar_colors)

    ax.set_ylabel('tCO2/year')
    ax.set_title('Carbon Emissions Comparisons (Energy and Process)')

    plt.savefig(data_dir / "Graphs/Total CO2 Emissions Benchmark.png")
    plt.close()
    # plt.show()

        # json dump
    with open(json_folder / "Cost_and_Emission_Input.json", 'w') as f:
        json.dump(cost_and_emissions_dict, f, indent=4)

    with open(json_folder / "Production_Input.json", 'w') as f:
        json.dump(production_input_dict, f, indent=4)

    with open(json_folder / "Electricity_Generation_Input.json", 'w') as f:
        json.dump(electricity_generation_input_dict, f, indent=4)

    with open(json_folder / "Energy_Input.json", 'w') as f:
        json.dump(energy_input_dict, f, indent=4)

    with open(json_folder / "Target_Input.json", 'w') as f:
        json.dump(target_dict, f, indent=4)

    with open(json_folder / "Detailed_Output.json", 'w') as f:
        json.dump(detailed_output_dict, f, indent=4)

    with open(json_folder / "Detailed_Output_Emissions.json", 'w') as f:
        json.dump(detailed_output_emissions_dict, f, indent=4)

    with open(json_folder / "Benchmarking_Results_Primary.json", 'w') as f:
        json.dump(benchmarking_results_primary_dict, f, indent=4)

    with open(json_folder / "Benchmarking_Results_Final.json", 'w') as f:
        json.dump(benchmarking_results_final_dict, f, indent=4)
        
    with open(json_folder / "Benchmarking_Results_CO2.json", 'w') as f:
        json.dump(benchmarking_results_co2_dict, f, indent=4)

    with open(json_folder / "Carbon_Capture_Input.json", 'r') as f:
        carbon_capture_dict = json.load(f)

    with open(json_folder / "Energy_Billing_Input.json", 'r') as f:
        energy_billing_input_dict = json.load(f)

    # Convert to dataframe
    # df_cost_and_emissions = pd.DataFrame.from_dict(cost_and_emissions_dict, orient='index')
    df_cost_and_emissions = pd.json_normalize(cost_and_emissions_dict, sep='-').T # just for reference
    df_cost_and_emissions.index.name = 'index'

    def convert_dict_to_excel(name_of_dict, name_of_sheet):
        df = pd.json_normalize(name_of_dict, sep='-').T
        df.name = 'index'
        return df


    sheets_dict = {
        'Cost and Emission Input': cost_and_emissions_dict,
        'Production Input': production_input_dict,
        'Carbon Capture': carbon_capture_dict,
        'Electricity Generation Input': electricity_generation_input_dict,
        'Energy Input': energy_input_dict,
        'Energy Billing Input': energy_billing_input_dict,
        'Target': target_dict,
        'Detailed Output': detailed_output_dict,
        'Detailed Output Emissions': detailed_output_emissions_dict,
        'Benchmarking Results Primary': benchmarking_results_primary_dict,
        'Benchmarking Results Final': benchmarking_results_final_dict,
        'Benchmarking Results CO2': benchmarking_results_co2_dict
        }

    with pd.ExcelWriter(json_folder / "report_in_excel.xlsx") as writer:
        for sheet in sheets_dict.keys():
            dummy = convert_dict_to_excel(sheets_dict[sheet], sheet)
            dummy.to_excel(writer, sheet_name=sheet)

    # Add additional variables
    electricity_price = cost_and_emissions_dict["Cost of electricity in $/kWh"]
    fuel_price = cost_and_emissions_dict["Fuel Price"]

    # Benchmarking by process
    def process_energy_group(facility, energy_form):
        raw_material_prepration_electricty = (detailed_output_dict["Preblending"][facility] + detailed_output_dict["Crushing"][facility] + detailed_output_dict["Grinding"][facility] + detailed_output_dict["Homogenization"][facility])
        fuel_preparation_electricity = detailed_output_dict["Fuel preparation"][facility]
        additive_prepration_electricity = detailed_output_dict["Additive prepration"][facility]
        additive_prepration_fuel = detailed_output_dict["Additive drying"][facility]
        kiln_mechanical_electricity = detailed_output_dict['Total kiln mechanical electricity'][facility]
        kiln_thermal_fuel = detailed_output_dict['Total for clinker making fuel'][facility]
        cement_grinding_electricity = detailed_output_dict['Cement grinding'][facility]
        other_production_electricity = detailed_output_dict["Total Electricity - Production - other"][facility]
        non_production_electricity = detailed_output_dict["Non-production energy use"][facility]
        
        raw_material_prepration_final = raw_material_prepration_electricty*3.6/10**6  # convert MJ into TJ
        fuel_preparation_final = fuel_preparation_electricity*3.6/10**6 
        additive_prepration_final = (additive_prepration_electricity*3.6 + additive_prepration_fuel)/10**6 
        kiln_mechanical_final = kiln_mechanical_electricity*3.6/10**6 
        kiln_thermal_final = kiln_thermal_fuel/10**6 
        cement_grinding_final = cement_grinding_electricity*3.6/10**6 
        other_production_final = other_production_electricity*3.6/10**6 
        non_production_final = non_production_electricity*3.6/10**6 
        
        raw_material_prepration_primary = (raw_material_prepration_electricty*3.6/0.305)/10**6 
        fuel_preparation_primary = (fuel_preparation_electricity*3.6/0.305)/10**6 
        additive_prepration_primary = (additive_prepration_electricity*3.6/0.305 + additive_prepration_fuel)/10**6 
        kiln_mechanical_primary = (kiln_mechanical_electricity*3.6/0.305)/10**6 
        kiln_thermal_primary = kiln_thermal_fuel/10**6 
        cement_grinding_primary = (cement_grinding_electricity*3.6/0.305)/10**6 
        other_production_primary = (other_production_electricity*3.6/0.305)/10**6 
        non_production_primary = (non_production_electricity*3.6/0.305)/10**6 
        
        raw_material_prepration_cost = raw_material_prepration_electricty*electricity_price
        fuel_preparation_cost = fuel_preparation_electricity*electricity_price
        additive_prepration_cost = additive_prepration_electricity*electricity_price + additive_prepration_fuel*fuel_price
        kiln_mechanical_cost = kiln_mechanical_electricity*electricity_price
        kiln_thermal_cost = kiln_thermal_fuel*fuel_price
        cement_grinding_cost = cement_grinding_electricity*electricity_price
        other_production_cost = other_production_electricity*electricity_price
        non_production_cost = non_production_electricity*electricity_price
        
        list_of_process_energy = []
        
        if energy_form == "final":
            list_of_process_energy = [raw_material_prepration_final, 
                                    fuel_preparation_final,
                                    additive_prepration_final,
                                    kiln_mechanical_final,
                                    kiln_thermal_final,
                                    cement_grinding_final,
                                    other_production_final,
                                    non_production_final]
        elif energy_form == "primary":
            list_of_process_energy = [raw_material_prepration_primary, 
                                    fuel_preparation_primary,
                                    additive_prepration_primary,
                                    kiln_mechanical_primary,
                                    kiln_thermal_primary,
                                    cement_grinding_primary,
                                    other_production_primary,
                                    non_production_primary]
        elif energy_form == "cost":
            list_of_process_energy = [raw_material_prepration_cost, 
                                    fuel_preparation_cost,
                                    additive_prepration_cost,
                                    kiln_mechanical_cost,
                                    kiln_thermal_cost,
                                    cement_grinding_cost,
                                    other_production_cost,
                                    non_production_cost]
        
        
        return list_of_process_energy # in TJ

    barWidth = 0.25
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True) 

    own_facility = process_energy_group("Your Facility", "final")
    IBP_facility = process_energy_group("International Best Practice Facility", "final")

    processes = ["Raw Material Preparation", "Fuel Preparation", "Additives Preparation", "Kiln - Machinery Use", "Kiln - Clinker Making", "Cement Grinding", "Other Production Energy", "Other Non-Prodution Energy"]

    x = np.arange(len(processes))

    ax.bar(x - barWidth/2, own_facility, barWidth, color='red')
    ax.bar(x + barWidth/2, IBP_facility, barWidth, color='green')
    plt.title('Benchmarking by Process')
    plt.xlabel('Process')
    plt.ylabel('Final Energy (TJ)')
    ax.set_xticks(x + barWidth, processes)
    plt.setp(ax.get_xticklabels(), fontsize=10, rotation='vertical')

    plt.savefig(data_dir / "Graphs/energy benchmark by process.png")
    plt.close()
    # plt.show()

    # Benchmark by process normalized
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    own_facility_array = np.array(own_facility)
    IBP_facility_array = np.array(IBP_facility)
    normalized_array = own_facility_array / IBP_facility_array
    normalized_list = list(normalized_array)

    processes = ["Raw Material Preparation", "Fuel Preparation", "Additives Preparation", "Kiln - Machinery Use", "Kiln - Clinker Making", "Cement Grinding", "Other Production Energy", "Other Non-Prodution Energy"]

    x = np.arange(len(processes))

    plt.bar(processes, normalized_list, color='green')
    plt.title('Benchmarking by Process')
    plt.xlabel('Process')
    plt.ylabel('Ratio of your facility to the best facility')
    plt.xticks(rotation=90)

    plt.savefig(data_dir / "Graphs/energy benchmark by process normalized.png")
    plt.close()
    # plt.show()

    # Final energy consumption
    fig, ax = plt.subplots(figsize=(7, 4))
    energy_mix = [Total_process_electricity*3.6, Total_process_fuel]
    energy_mix_labels = ["electricity", "fuel"]

    plt.pie(energy_mix, labels = energy_mix_labels)
    plt.title('Final Energy Consumption')
    plt.savefig(data_dir / "Graphs/final energy consumption.png")
    plt.close()
    # plt.show() 


    # Primary energy consumption
    fig, ax = plt.subplots(figsize=(7, 4))
    energy_mix = [Total_process_electricity*3.6/0.305, Total_process_fuel]
    energy_mix_labels = ["electricity", "fuel"]

    plt.pie(energy_mix, labels = energy_mix_labels)
    plt.title('Primary Energy Consumption')
    plt.savefig(data_dir / "Graphs/primary energy consumption.png")
    plt.close()
    # plt.show() 

    # Energy cost
    fig, ax = plt.subplots(figsize=(7, 4))
    energy_mix = [Total_process_electricity*0.2, Total_process_fuel*0.033]
    energy_mix_labels = ["electricity", "fuel"]

    plt.pie(energy_mix, labels = energy_mix_labels)
    plt.title('Energy Cost')
    plt.savefig(data_dir / "Graphs/energy cost.png")
    plt.close()
    # plt.show() 

    # Share of final energy by process step
    fig, ax = plt.subplots(figsize=(7, 4))
    process_energy = process_energy_group("Your Facility", "final")
    processes = ["Raw Material Preparation", "Fuel Preparation", "Additives Preparation", "Kiln - Machinery Use", "Kiln - Clinker Making", "Cement Grinding", "Other Production Energy", "Other Non-Prodution Energy"]

    plt.pie(process_energy)
    plt.title('Share of Final Energy by Process Step')
    plt.legend(loc='best', bbox_to_anchor=(-0.1, 1.),
            fontsize=8, labels = processes)
    plt.savefig(data_dir / "Graphs/final energy by process.png")
    plt.close()
    # plt.show() 

    # Share of primary energy by process step
    fig, ax = plt.subplots(figsize=(7, 4))
    process_energy = process_energy_group("Your Facility", "primary")
    processes = ["Raw Material Preparation", "Fuel Preparation", "Additives Preparation", "Kiln - Machinery Use", "Kiln - Clinker Making", "Cement Grinding", "Other Production Energy", "Other Non-Prodution Energy"]

    plt.pie(process_energy)
    plt.title('Share of Primary Energy by Process Step')
    plt.legend(loc='best', bbox_to_anchor=(-0.1, 1.),
            fontsize=8, labels = processes)
    plt.savefig(data_dir / "Graphs/primary energy by process.png")
    plt.close()
    # plt.show() 


    # Share of energy costs by process step
    fig, ax = plt.subplots(figsize=(7, 4))
    process_energy = process_energy_group("Your Facility", "cost")
    processes = ["Raw Material Preparation", "Fuel Preparation", "Additives Preparation", "Kiln - Machinery Use", "Kiln - Clinker Making", "Cement Grinding", "Other Production Energy", "Other Non-Prodution Energy"]

    plt.pie(process_energy)
    plt.title('Share of Energy Cost by Process Step')
    plt.legend(loc='best', bbox_to_anchor=(-0.1, 1.),
            fontsize=8, labels = processes)
    plt.savefig(data_dir / "Graphs/energy cost by process.png")
    plt.close()
    # plt.show() 

    return detailed_output_dict, international_best_practice_dict, benchmarking_results_final_dict, benchmarking_results_co2_dict


############################ 


def Page8_All_Measures_1_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    all_measures_dict = {
    "EE-RM Preparation": {
        "unit": {
            "Do you want to apply this measure?": "NaN",
            "Potential Application": "(%)",
            "Energy Consumption Share of Process": "% (of grinding energy, unless stated)",
            "Typical Energy Savings": "kWh/tonne raw materials",
            "Typical Investment per mass": "USD/tonne",
            "Typical Investments": "USD/kWh-saved",
            "Total Energy Savings": "%",
            "Total Energy Savings - Absolute": "kWh/year",
            "Total Costs": "USD",
            "Payback Period": "years",
            "Energy Type": "NaN",
            "Process": "NaN",
            "Abatement cost": "$/tCO2",
            "Total Emissions Reduction": "tCO2/year",
            "Total Emissions Reduction - direct": "tCO2/year",
            "Total Emissions Reduction - indirect": "tCO2/year"
        },
        "Wash Mills with Closed Circuit Classifier (Wet Process)": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.40516206482593037,
            "Typical Energy Savings": 6,
            "Typical Investment per mass": 0,
            "Typical Investments": 0.0,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 1620000.0,
            "Total Costs": 0.0,
            "Payback Period": "immediate",
            "Energy Type": "Electricity",
            "Process": "Grinding",
            "Abatement cost": 400.0,
            "Total Emissions Reduction": 846.5861344537816,
            "Total Emissions Reduction - indirect": 767.4579831932773,
            "Total Emissions Reduction - direct": 79.12815126050425
        },
        "Raw Meal Process Control (Dry process - Vertical Mill)": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.06077430972388956,
            "Typical Energy Savings": 0.9,
            "Typical Investment per mass": 0.3,
            "Typical Investments": 0.3333333333333333,
            "Total Energy Savings": 0.06077430972388956,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Grinding",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "High-efficiency classifiers/separators (Dry process)": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.2194627851140456,
            "Typical Energy Savings": 3.25,
            "Typical Investment per mass": 2.2000000000000006,
            "Typical Investments": 0.6769230769230771,
            "Total Energy Savings": 0.2194627851140456,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Grinding",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Use of Roller Mills (Dry Process)": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.4389255702280912,
            "Typical Energy Savings": 6.5,
            "Typical Investment per mass": 5.5,
            "Typical Investments": 0.8461538461538461,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Grinding",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Efficient transport systems (Dry process)": {
            "Do you want to apply this measure?": "Yes, Partially",
            "Potential Application": 0.0,
            "Energy Consumption Share of Process": 0.13505402160864347,
            "Typical Energy Savings": 2,
            "Typical Investment per mass": 3,
            "Typical Investments": 1.5,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Grinding",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Raw Meal Blending (Homogenizing) Systems (Dry Process)": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 1,
            "Typical Energy Savings": 1.5,
            "Typical Investment per mass": 3.7,
            "Typical Investments": 2.466666666666667,
            "Total Energy Savings": 0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Preblending",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        }
    },
    "EE-Fuel Preparation": {
        "unit": {
            "Do you want to apply this measure?": "NaN",
            "Potential Application": "(%)",
            "Energy Consumption Share of Process": "% Fuel grinding energy",
            "Typical Energy Savings": "kWh/tonne",
            "Typical Investment per mass": "USD/tonne",
            "Typical Investments": "USD/kWh-saved",
            "Total Energy Savings": "% Fuel grinding energy use",
            "Total Energy Savings - Absolute": "kWh/year",
            "Total Costs": "USD",
            "Payback Period": "years",
            "Energy Type": "NaN",
            "Process": "NaN",
            "Abatement cost": "$/tCO2",
            "Total Emissions Reduction": "tCO2/year",
            "Total Emissions Reduction - direct": "tCO2/year",
            "Total Emissions Reduction - indirect": "tCO2/year"
        },
        "New Efficient Coal Separator for Fuel Preparation": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.08532435883860975,
            "Typical Energy Savings": 2.98969072164948,
            "Typical Investment per mass": 0.010666666666666663,
            "Typical Investments": 0.003567816091954027,
            "Total Energy Savings": 0.08532435883860975,
            "Total Energy Savings - Absolute": 48737.27376861389,
            "Total Costs": 173.88562962962953,
            "Payback Period": 0.017839080459770135,
            "Energy Type": "Electricity",
            "Process": "Fuel preparation",
            "Abatement cost": 400.35678160919537,
            "Total Emissions Reduction": 25.469321113325016,
            "Total Emissions Reduction - indirect": 23.088771501727802,
            "Total Emissions Reduction - direct": 2.3805496115972136
        },
        "Conversion to efficient roller mills": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.2425859788359788,
            "Typical Energy Savings": 8.5,
            "Typical Investment per mass": 0.25,
            "Typical Investments": 0.029411764705882353,
            "Total Energy Savings": 0.2425859788359788,
            "Total Energy Savings - Absolute": 126742.13184815482,
            "Total Costs": 3727.7097602398476,
            "Payback Period": 0.14705882352941174,
            "Energy Type": "Electricity",
            "Process": "Fuel preparation",
            "Abatement cost": 402.94117647058823,
            "Total Emissions Reduction": 66.23341448997589,
            "Total Emissions Reduction - indirect": 60.04275363814899,
            "Total Emissions Reduction - direct": 6.190660851826894
        }
    },
    "EE-Kiln": {
        "unit": {
            "Do you want to apply this measure?": "NaN",
            "Potential Application": "(%)",
            "Energy Consumption Share of Process": "% of Kiln Energy Use",
            "Typical Energy Savings": "MJ or kWh/tonne",
            "Typical Investment per mass": "USD/tonne",
            "Typical Investments": "USD/MJ or kWh-saved",
            "Total Energy Savings": "% of Kiln Energy Use",
            "Total Energy Savings - Absolute": "MJ or kWh/year",
            "Total Costs": "USD",
            "Payback Period": "years",
            "Energy Type": "NaN",
            "Process": "NaN",
            "Abatement cost": "$/tCO2",
            "Total Emissions Reduction": "tCO2/year",
            "Total Emissions Reduction - direct": "tCO2/year",
            "Total Emissions Reduction - indirect": "tCO2/year"
        },
        "Fan modifications": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.0011936592818945762,
            "Typical Energy Savings": 0.05,
            "Typical Investment per mass": 0.0003,
            "Typical Investments": 0.005999999999999999,
            "Total Energy Savings": 0.0011936592818945762,
            "Total Energy Savings - Absolute": 5000.000000000001,
            "Total Costs": 30.0,
            "Payback Period": 0.029999999999999995,
            "Energy Type": "Electricity",
            "Process": "Kiln mechanical",
            "Abatement cost": 400.6,
            "Total Emissions Reduction": 2.6129201680672276,
            "Total Emissions Reduction - indirect": 2.368697478991597,
            "Total Emissions Reduction - direct": 0.24422268907563044
        },
        "Improved refractories ": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.12276133844692337,
            "Typical Energy Savings": 500.12969283276584,
            "Typical Investment per mass": 0.25,
            "Typical Investments": 0.0004998703407989723,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Energy management and process control systems": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.05,
            "Typical Energy Savings": 203.7,
            "Typical Investment per mass": 0.35,
            "Typical Investments": 0.001718213058419244,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Adjustable speed drive for kiln fan": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.14562643239113826,
            "Typical Energy Savings": 6.1,
            "Typical Investment per mass": 1.1875,
            "Typical Investments": 0.194672131147541,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Kiln mechanical",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Seal replacement": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.004,
            "Typical Energy Savings": 16.296,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.008532423208191127,
            "Total Energy Savings": 0.004,
            "Total Energy Savings - Absolute": 1629600.0,
            "Total Costs": 13904.43686006826,
            "Payback Period": 0.2559726962457338,
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": 363.0102633735795,
            "Total Emissions Reduction": 151.5528,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 151.5528
        },
        "Grate cooler optimization": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.035,
            "Typical Energy Savings": 142.59000000000003,
            "Typical Investment per mass": 0.22,
            "Typical Investments": 0.0015428851953152392,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Optimize heat recovery in clinker cooler": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.01964181415150769,
            "Typical Energy Savings": 80.02075085324232,
            "Typical Investment per mass": 0.22,
            "Typical Investments": 0.002749286874394355,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Kiln combustion system improvements": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.06,
            "Typical Energy Savings": 244.44,
            "Typical Investment per mass": 1.0000000000000002,
            "Typical Investments": 0.0040909834724267725,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Low temperature heat recovery for power generation": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 1,
            "Typical Energy Savings": 45,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.83,
            "Total Energy Savings": 1,
            "Total Energy Savings - Absolute": 4183800.0,
            "Total Costs": 3472554.0,
            "Payback Period": 4.1499999999999995,
            "Energy Type": "Electricity",
            "Process": "Kiln mechanical",
            "Abatement cost": 483.0,
            "Total Emissions Reduction": 2186.387079831933,
            "Total Emissions Reduction - indirect": 1982.0313025210085,
            "Total Emissions Reduction - direct": 204.35577731092448
        },
        "High temperature heat recovery for power generation": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.5252100840336135,
            "Typical Energy Savings": 22,
            "Typical Investment per mass": 3.3,
            "Typical Investments": 0.15,
            "Total Energy Savings": 0.5252100840336135,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Kiln mechanical",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Conversion to reciprocating grate cooler": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.08,
            "Typical Energy Savings": 325.92,
            "Typical Investment per mass": 3,
            "Typical Investments": 0.009204712812960236,
            "Total Energy Savings": 0.08,
            "Total Energy Savings - Absolute": 32461632.0,
            "Total Costs": 298800.0,
            "Payback Period": 0.2761413843888071,
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": 363.3717093976489,
            "Total Emissions Reduction": 3018.931776,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 3018.931776
        },
        "Efficient kiln drives": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.013130252100840338,
            "Typical Energy Savings": 0.55,
            "Typical Investment per mass": 0.2,
            "Typical Investments": 0.36363636363636365,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Kiln mechanical",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Conversion of long dry kilns to preheater/precalciner kiln": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.3437317476513845,
            "Typical Energy Savings": 1400.3631399317403,
            "Typical Investment per mass": 28,
            "Typical Investments": 0.01999481363195895,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Upgrading the preheater from 5 to 6 stages": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.02621859697645403,
            "Typical Energy Savings": 106.81456408207372,
            "Typical Investment per mass": 2.54,
            "Typical Investments": 0.023779528773326508,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Dry process upgrade to multi-stage preheater kiln": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.22097040920446184,
            "Typical Energy Savings": 900.2334470989775,
            "Typical Investment per mass": 30,
            "Typical Investments": 0.03332468938659819,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Upgrading of a preheater to a preheater/precalciner kiln": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.09820907075753843,
            "Typical Energy Savings": 400.1037542662116,
            "Typical Investment per mass": 16.5,
            "Typical Investments": 0.04123930311591533,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Low pressure drop cyclones": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.02100840336134454,
            "Typical Energy Savings": 0.88,
            "Typical Investment per mass": 3,
            "Typical Investments": 3.409090909090909,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Process": "Kiln mechanical",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Indirect firing ": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.00454216952253615,
            "Typical Energy Savings": 18.504798634812275,
            "Typical Investment per mass": 7.4,
            "Typical Investments": 0.3998962726391792,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Conversion to new suspension preheater/precalciner kiln": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.5892544245452305,
            "Typical Energy Savings": 2400.622525597269,
            "Typical Investment per mass": 28,
            "Typical Investments": 0.011663641285309388,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Process": "Kiln thermal",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        }
    },
    "EE-Cement Grinding": {
        "unit": {
            "Do you want to apply this measure?": "NaN",
            "Potential Application": "(%)",
            "Energy Consumption Share of Process": "% Grinding Energy Use",
            "Typical Energy Savings": "kWh/tonne",
            "Typical Investment per mass": "USD/tonne",
            "Typical Investments": "USD/kWh-saved",
            "Total Energy Savings": "% Grinding Energy Use",
            "Total Energy Savings - Absolute": "kWh/year",
            "Total Costs": "RMB",
            "Payback Period": "years",
            "Energy Type": "NaN",
            "Abatement cost": "$/tCO2",
            "Total Emissions Reduction": "tCO2/year",
            "Total Emissions Reduction - direct": "tCO2/year",
            "Total Emissions Reduction - indirect": "tCO2/year"
        },
        "Energy management and process control": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.05,
            "Typical Energy Savings": 3.19872,
            "Typical Investment per mass": 0.18,
            "Typical Investments": 0.056272509003601444,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Improved grinding mill (horozontal mill)": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.1750700280112045,
            "Typical Energy Savings": 11.200000000000001,
            "Typical Investment per mass": 4,
            "Typical Investments": 0.3571428571428571,
            "Total Energy Savings": 0.1750700280112045,
            "Total Energy Savings - Absolute": 1400000.0000000002,
            "Total Costs": 500000.0,
            "Payback Period": 1.7857142857142854,
            "Energy Type": "Electricity",
            "Abatement cost": 435.7142857142857,
            "Total Emissions Reduction": 731.6176470588238,
            "Total Emissions Reduction - indirect": 663.2352941176472,
            "Total Emissions Reduction - direct": 68.38235294117653
        },
        "Improved grinding media (ball mills)": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.0625250100040016,
            "Typical Energy Savings": 4,
            "Typical Investment per mass": 1.8,
            "Typical Investments": 0.45,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "High efficiency classifiers": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.0547093837535014,
            "Typical Energy Savings": 3.5,
            "Typical Investment per mass": 2,
            "Typical Investments": 0.5714285714285714,
            "Total Energy Savings": 0.0547093837535014,
            "Total Energy Savings - Absolute": 360906.862745098,
            "Total Costs": 206232.49299719886,
            "Payback Period": 2.8571428571428568,
            "Energy Type": "Electricity",
            "Abatement cost": 457.1428571428572,
            "Total Emissions Reduction": 188.60416409210742,
            "Total Emissions Reduction - indirect": 170.97583518701597,
            "Total Emissions Reduction - direct": 17.62832890509146
        }
    },
    "EE-Product&Feedstock Changes": {
        "unit": {
            "Do you want to apply this measure?": "NaN",
            "Potential Application": "(%)",
            "Energy Consumption Share of Process": "% of Kiln Energy Use",
            "Typical Energy Savings": "MJ/tonne clinker",
            "Typical Investment per mass": "USD/tonne",
            "Typical Investments": "USD/MJ-saved",
            "Total Energy Savings": "% of Kiln Energy Use",
            "Total Energy Savings - Absolute": "MJ/year",
            "Total Costs": "USD",
            "Payback Period": "years",
            "Energy Type": "NaN",
            "Abatement cost": "$/tCO2",
            "Total Emissions Reduction": "tCO2/year",
            "Total Emissions Reduction - direct": "tCO2/year",
            "Total Emissions Reduction - indirect": "tCO2/year"
        },
        "Low alkali cement": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.005155976214770771,
            "Typical Energy Savings": 21.00544709897612,
            "Typical Investment per mass": 0,
            "Typical Investments": 0.0,
            "Total Energy Savings": 0.005155976214770771,
            "Total Energy Savings - Absolute": 1924771.12857338,
            "Total Costs": 0.0,
            "Payback Period": "immediate",
            "Energy Type": "Fuel",
            "Abatement cost": 358.4229390681004,
            "Total Emissions Reduction": 179.00371495732432,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 179.00371495732432
        },
        "Blended cements": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.3437317476513845,
            "Typical Energy Savings": 1400.3631399317403,
            "Typical Investment per mass": 0.72,
            "Typical Investments": 0.0005141523505360873,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Use of waste-derived fuels": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.14731360613630762,
            "Typical Energy Savings": 600.1556313993173,
            "Typical Investment per mass": 1.1,
            "Typical Investments": 0.001832857916262904,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Limestone cement": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.05,
            "Typical Energy Savings": 203.7,
            "Typical Investment per mass": 0.72,
            "Typical Investments": 0.0035346097201767305,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Use of steel slag in kiln (CemStar)": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.046637211585665195,
            "Typical Energy Savings": 190,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.02631578947368421,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Fuel",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0,
            "Total Emissions Reduction - direct": 0.0
        }
    },
    "EE-Utility Systems": {
        "unit": {
            "Do you want to apply this measure?": "NaN",
            "Potential Application": "(%)",
            "Energy Consumption Share of Process": "% of Electricity Use ",
            "Typical Energy Savings": "kWh/tonne",
            "Typical Investment per mass": "USD/tonne",
            "Typical Investments": "USD/kWh",
            "Total Energy Savings": "% of Electricity or Fuel Use",
            "Total Energy Savings - Absolute": "kWh/year",
            "Total Costs": "USD",
            "Payback Period": "years",
            "Energy Type": "NaN",
            "Abatement cost": "$/tCO2",
            "Total Emissions Reduction": "tCO2/year",
            "Total Emissions Reduction - direct": "tCO2/year",
            "Total Emissions Reduction - indirect": "tCO2/year"
        },
        "High efficiency fans": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.0026260504201680674,
            "Typical Energy Savings": 0.4,
            "Typical Investment per mass": 0.009333333333333334,
            "Typical Investments": 0.023333333333333334,
            "Total Energy Savings": 0.0026260504201680674,
            "Total Energy Savings - Absolute": 29660.750345688368,
            "Total Costs": 692.0841747327286,
            "Payback Period": 0.11666666666666667,
            "Energy Type": "Electricity",
            "Abatement cost": 402.3333333333334,
            "Total Emissions Reduction": 15.500234555651222,
            "Total Emissions Reduction - indirect": 14.051468913766232,
            "Total Emissions Reduction - direct": 1.4487656418849895
        },
        "High efficiency motors": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.03174894957983194,
            "Typical Energy Savings": 4.836,
            "Typical Investment per mass": 0.22,
            "Typical Investments": 0.045492142266335814,
            "Total Energy Savings": 0.03174894957983194,
            "Total Energy Savings - Absolute": 357656.77401214716,
            "Total Costs": 16270.572845879316,
            "Payback Period": 0.22746071133167906,
            "Energy Type": "Electricity",
            "Abatement cost": 404.5492142266336,
            "Total Emissions Reduction": 186.90571961244035,
            "Total Emissions Reduction - indirect": 169.436139789368,
            "Total Emissions Reduction - direct": 17.469579823072326
        },
        "Variable speed drives in fan systems": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.026260504201680673,
            "Typical Energy Savings": 4,
            "Typical Investment per mass": 1,
            "Typical Investments": 0.25,
            "Total Energy Savings": 0.026260504201680673,
            "Total Energy Savings - Absolute": 286436.3499811002,
            "Total Costs": 71609.08749527505,
            "Payback Period": 1.25,
            "Energy Type": "Electricity",
            "Abatement cost": 425.0,
            "Total Emissions Reduction": 149.68706314663586,
            "Total Emissions Reduction - indirect": 135.69621201835733,
            "Total Emissions Reduction - direct": 13.990851128278537
        },
        "Reduce leaks": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.2,
            "Typical Energy Savings": 1.52,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.04,
            "Total Energy Savings": 0.2,
            "Total Energy Savings - Absolute": 190000.0,
            "Total Costs": 7600.0,
            "Payback Period": 0.19999999999999998,
            "Energy Type": "Electricity",
            "Abatement cost": 404.0,
            "Total Emissions Reduction": 99.29096638655463,
            "Total Emissions Reduction - indirect": 90.01050420168067,
            "Total Emissions Reduction - direct": 9.280462184873956
        },
        "Maintenance of compressed air systems": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.15,
            "Typical Energy Savings": 1.14,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.06,
            "Total Energy Savings": 0.15,
            "Total Energy Savings - Absolute": 142500.0,
            "Total Costs": 8550.0,
            "Payback Period": 0.3,
            "Energy Type": "Electricity",
            "Abatement cost": 406.0,
            "Total Emissions Reduction": 74.46822478991596,
            "Total Emissions Reduction - indirect": 67.5078781512605,
            "Total Emissions Reduction - direct": 6.9603466386554675
        },
        "Heat recovery for water preheating": {
            "Do you want to apply this measure?": "Yes (100%)",
            "Potential Application": 1,
            "Energy Consumption Share of Process": 0.2,
            "Typical Energy Savings": 1.52,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.13333333333333333,
            "Total Energy Savings": 0.2,
            "Total Energy Savings - Absolute": 190000.0,
            "Total Costs": 25333.333333333332,
            "Payback Period": 0.6666666666666666,
            "Energy Type": "Electricity",
            "Abatement cost": 413.33333333333337,
            "Total Emissions Reduction": 99.29096638655463,
            "Total Emissions Reduction - indirect": 90.01050420168067,
            "Total Emissions Reduction - direct": 9.280462184873956
        },
        "Reducing inlet air temperature": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.02,
            "Typical Energy Savings": 0.152,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.17333333333333334,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Compressor controls": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.12,
            "Typical Energy Savings": 0.9119999999999999,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.25,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
        },
        "Sizing pipe diameter correctly": {
            "Do you want to apply this measure?": "No (0%)",
            "Potential Application": 0,
            "Energy Consumption Share of Process": 0.03,
            "Typical Energy Savings": 0.22799999999999998,
            "Typical Investment per mass": "NaN",
            "Typical Investments": 0.5,
            "Total Energy Savings": 0.0,
            "Total Energy Savings - Absolute": 0.0,
            "Total Costs": 0.0,
            "Payback Period": "-",
            "Energy Type": "Electricity",
            "Abatement cost": "N/A",
            "Total Emissions Reduction": 0.0,
            "Total Emissions Reduction - indirect": 0.0,
            "Total Emissions Reduction - direct": 0.0
            }
        }
    }

    page8_all_measures_map = {
    "EE-RM Preparation": {
        "Wash Mills with Closed Circuit Classifier (Wet Process)": {
            "comboBox": "page8_1_comboBox",
            "input": "page8_1_potential_input",
        },
        "Raw Meal Process Control (Dry process - Vertical Mill)": {
            "comboBox": "page8_1_comboBox_2",
            "input": "page8_1_potential_input_2",
        },
        "High-efficiency classifiers/separators (Dry process)": {
            "comboBox": "page8_1_comboBox_3",
            "input": "page8_1_potential_input_3",
        },
        "Use of Roller Mills (Dry Process)": {
            "comboBox": "page8_1_comboBox_4",
            "input": "page8_1_potential_input_4",
        },
        "Efficient transport systems (Dry process)": {
            "comboBox": "page8_1_comboBox_5",
            "input": "page8_1_potential_input_5",
        },
        "Raw Meal Blending (Homogenizing) Systems (Dry Process)": {
            "comboBox": "page8_1_comboBox_12",
            "input": "page8_1_potential_input_12",
        },
    },
    "EE-Fuel Preparation": {
        "New Efficient Coal Separator for Fuel Preparation": {
            "comboBox": "page8_1_comboBox_6",
            "input": "page8_1_potential_input_6",
        },
        "Conversion to efficient roller mills": {
            "comboBox": "page8_1_comboBox_7",
            "input": "page8_1_potential_input_7",
        },
    },
    "EE-Cement Grinding": {
        "Energy management and process control": {
            "comboBox": "page8_1_comboBox_8",
            "input": "page8_1_potential_input_8",
        },
        "Improved grinding mill (horozontal mill)": { 
            "comboBox": "page8_1_comboBox_9",
            "input": "page8_1_potential_input_9",
        },
        "Improved grinding media (ball mills)": {
            "comboBox": "page8_1_comboBox_10",
            "input": "page8_1_potential_input_10",
        },
        "High efficiency classifiers": { 
            "comboBox": "page8_1_comboBox_11",
            "input": "page8_1_potential_input_11",
        },
    }}



    for unit, measures in page8_all_measures_map.items():
        print("this is the unit", unit)
        print("this is the measures", measures)
        for measure, widgets in measures.items():
            print("this is the measure", measure)
            print("this is the widgets", widgets)

            print("this is the default value in the dict", all_measures_dict[unit][measure]["Do you want to apply this measure?"])
            print("this is the default value in the dict", all_measures_dict[unit][measure]["Potential Application"])

            combo = getattr(self.ui, widgets["comboBox"])
            choice = combo.currentText()

            input_widget = getattr(self.ui, widgets["input"])
            input_text = input_widget.text().strip()

            # default to 0 if empty, otherwise convert to float
            input_value = float(input_text) if input_text else 0

            print("this is the choice", choice)
            print("this is the input value", input_value)

            if choice in ["Yes (100%)", "No (0%)"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = 1 if "Yes" in choice else 0
            elif choice in ["Yes, Partially"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = input_value
            

            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Do you want to apply this measure?"])
            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Potential Application"])

    with open(json_folder / "all_measures.json", "w") as f:
        json.dump(all_measures_dict, f)

    print("page 8_1 all done")

    return all_measures_dict 

def Page8_All_Measures_2a_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    with open(json_folder / "all_measures.json", "r") as f:
        all_measures_dict = json.load(f)

    page8_all_measures_2a_map = {
    "EE-Kiln": {
        "Fan modifications": {
            "comboBox": "page_8_2a_comboBox",
            "input": "page_8_2a_input",
        },
        "Improved refractories ": {  # notice trailing space kept to match first dict
            "comboBox": "page_8_2a_comboBox_2",
            "input": "page_8_2a_input_2",
        },
        "Energy management and process control systems": {
            "comboBox": "page_8_2a_comboBox_3",
            "input": "page_8_2a_input_3",
        },
        "Adjustable speed drive for kiln fan": {
            "comboBox": "page_8_2a_comboBox_4",
            "input": "page_8_2a_input_4",
        },
        "Seal replacement": {
            "comboBox": "page_8_2a_comboBox_5",
            "input": "page_8_2a_input_5",
        },
        "Grate cooler optimization": {
            "comboBox": "page_8_2a_comboBox_6",
            "input": "page_8_2a_input_6",
        },
        "Optimize heat recovery in clinker cooler": {
            "comboBox": "page_8_2a_comboBox_7",
            "input": "page_8_2a_input_7",
        },
        "Kiln combustion system improvements": {
            "comboBox": "page_8_2a_comboBox_8",
            "input": "page_8_2a_input_8",
        },
        "Low temperature heat recovery for power generation": {
            "comboBox": "page_8_2a_comboBox_9",
            "input": "page_8_2a_input_9",
        },
        }
    }


    for unit, measures in page8_all_measures_2a_map.items():
        print("this is the unit", unit)
        print("this is the measures", measures)
        for measure, widgets in measures.items():
            print("this is the measure", measure)
            print("this is the widgets", widgets)

            print("this is the default value in the dict", all_measures_dict[unit][measure]["Do you want to apply this measure?"])
            print("this is the default value in the dict", all_measures_dict[unit][measure]["Potential Application"])

            combo = getattr(self.ui, widgets["comboBox"])
            choice = combo.currentText()

            input_widget = getattr(self.ui, widgets["input"])
            input_text = input_widget.text().strip()

            # default to 0 if empty, otherwise convert to float
            input_value = float(input_text) if input_text else 0

            if choice in ["Yes (100%)", "No (0%)"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = 1 if "Yes" in choice else 0
            elif choice in ["Yes, Partially"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = input_value

            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Do you want to apply this measure?"])
            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Potential Application"])

    with open(json_folder / "all_measures.json", "w") as f:
        json.dump(all_measures_dict, f)

    print("page 8_2a all done")

    return all_measures_dict 

def Page8_All_Measures_2b_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    with open(json_folder / "all_measures.json", "r") as f:
        all_measures_dict = json.load(f)

    page8_all_measures_2b_map = {
    "EE-Kiln": {
        "High temperature heat recovery for power generation": {
            "comboBox": "page_8_2b_comboBox",
            "input": "page_8_2b_input",
        },
        "Conversion to reciprocating grate cooler": {
            "comboBox": "page_8_2b_comboBox_2",
            "input": "page_8_2b_input_2",
        },
        "Efficient kiln drives": {
            "comboBox": "page_8_2b_comboBox_3",
            "input": "page_8_2b_input_3",
        },
        "Conversion of long dry kilns to preheater/precalciner kiln": {
            "comboBox": "page_8_2b_comboBox_4",
            "input": "page_8_2b_input_4",
        },
        "Upgrading the preheater from 5 to 6 stages": {
            "comboBox": "page_8_2b_comboBox_5",
            "input": "page_8_2b_input_5",
        },
        "Dry process upgrade to multi-stage preheater kiln": {
            "comboBox": "page_8_2b_comboBox_6",
            "input": "page_8_2b_input_6",
        },
        "Low pressure drop cyclones": {
            "comboBox": "page_8_2b_comboBox_7",
            "input": "page_8_2b_input_7",
        },
        "Indirect firing ": {  # note: trailing space in first dict is preserved
            "comboBox": "page_8_2b_comboBox_8",
            "input": "page_8_2b_input_8",
        },
        "Conversion to new suspension preheater/precalciner kiln": {  
            "comboBox": "page_8_2b_comboBox_9",
            "input": "page_8_2b_input_9",
        },
    }
    }

    for unit, measures in page8_all_measures_2b_map.items():
        for measure, widgets in measures.items():

            combo = getattr(self.ui, widgets["comboBox"])
            choice = combo.currentText()

            input_widget = getattr(self.ui, widgets["input"])
            input_text = input_widget.text().strip()

            # default to 0 if empty, otherwise convert to float
            input_value = float(input_text) if input_text else 0

            if choice in ["Yes (100%)", "No (0%)"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = 1 if "Yes" in choice else 0
            elif choice in ["Yes, Partially"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = input_value

            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Do you want to apply this measure?"])
            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Potential Application"])

    with open(json_folder / "all_measures.json", "w") as f:
        json.dump(all_measures_dict, f)

    print("page 8_2b all done")

    return all_measures_dict 

def Page8_All_Measures_3_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    with open(json_folder / "all_measures.json", "r") as f:
        all_measures_dict = json.load(f)

    page8_all_measures_3_map = {
    "EE-Product&Feedstock Changes": {
        "Low alkali cement": {
            "comboBox": "page_8_3_comboBox",
            "input": "page_8_3_input",
        },
        "Blended cements": {
            "comboBox": "page_8_3_comboBox_2",
            "input": "page_8_3_input_2",
        },
        "Use of waste-derived fuels": {
            "comboBox": "page_8_3_comboBox_3",
            "input": "page_8_3_input_3",
        },
        "Limestone cement": {
            "comboBox": "page_8_3_comboBox_4",
            "input": "page_8_3_input_4",
        },
        "Use of steel slag in kiln (CemStar)": {
            "comboBox": "page_8_3_comboBox_5",
            "input": "page_8_3_input_5",
        },
    },
    "EE-Utility Systems": {
        "High efficiency fans": {
            "comboBox": "page_8_3_comboBox_6",
            "input": "page_8_3_input_6",
        },
        "High efficiency motors": {
            "comboBox": "page_8_3_comboBox_7",
            "input": "page_8_3_input_7",
        },
        "Variable speed drives in fan systems": {
            "comboBox": "page_8_3_comboBox_8",
            "input": "page_8_3_input_8",
        },
        "Reduce leaks": {
            "comboBox": "page_8_3_comboBox_9",
            "input": "page_8_3_input_9",
        },
        "Maintenance of compressed air systems": {
            "comboBox": "page_8_3_comboBox_10",
            "input": "page_8_3_input_10",
        },
        "Heat recovery for water preheating": {
            "comboBox": "page_8_3_comboBox_11",
            "input": "page_8_3_input_11",
        },
        "Reducing inlet air temperature": {
            "comboBox": "page_8_3_comboBox_12",
            "input": "page_8_3_input_12",
        },
        "Compressor controls": {
            "comboBox": "page_8_3_comboBox_13",
            "input": "page_8_3_input_13",
        },
        "Sizing pipe diameter correctly": {
            "comboBox": "page_8_3_comboBox_14",
            "input": "page_8_3_input_14",
        },
        }
    }

    
    
    for unit, measures in page8_all_measures_3_map.items():
        for measure, widgets in measures.items():

            combo = getattr(self.ui, widgets["comboBox"])
            choice = combo.currentText()

            input_widget = getattr(self.ui, widgets["input"])
            input_text = input_widget.text().strip()

            # default to 0 if empty, otherwise convert to float
            input_value = float(input_text) if input_text else 0

            if choice in ["Yes (100%)", "No (0%)"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = 1 if "Yes" in choice else 0
            elif choice in ["Yes, Partially"]:
                all_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_measures_dict[unit][measure]["Potential Application"] = input_value

            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Do you want to apply this measure?"])
            print("this is what is saved in the dict", all_measures_dict[unit][measure]["Potential Application"])

    with open(json_folder / "all_measures.json", "w") as f:
        json.dump(all_measures_dict, f)

    print("page 8_3 all done")

    return all_measures_dict 

## EE Measure
def EE_measure(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    with open(json_folder / "all_measures.json", "r") as f:
        all_measures_dict = json.load(f)

    # Fill in measure order
    measure_order = {}
    apply_ordering = True

    # Automatically generate typical investments and potential applications
    def EE_measure_table(measures_data):   

        exception_measures = ["unit", "Use of steel slag in kiln (CemStar)", "Seal replacement", "Low temperature heat recovery for power generation"]
        for measure_cateogry in measures_data.keys():
            if measure_cateogry != "EE-Utility Systems":
                print(measure_cateogry)
                print(measures_data[measure_cateogry].keys())
                for measure in measures_data[measure_cateogry].keys():        
                        
                    # # These values are updated in Page 8 functions
                    # if measure != "unit":
                                    
                    #     if measures_data[measure_cateogry][measure]["Do you want to apply this measure?"] == "Yes (100%)":
                    #         measures_data[measure_cateogry][measure]["Potential Application"] = 1
                    #     elif measures_data[measure_cateogry][measure]["Do you want to apply this measure?"] == "No (0%)":
                    #         measures_data[measure_cateogry][measure]["Potential Application"] = 0
                    #     else:
                    #         measures_data[measure_cateogry][measure]["Potential Application"] = measures_data[measure_cateogry][measure]["Potential Application"]
                            
                    if measure not in exception_measures: # these are exceptions
                        print(measure_cateogry)
                        print(measure)
                        print(measures_data[measure_cateogry][measure]["Typical Investment per mass"])
                        print(measures_data[measure_cateogry][measure]["Typical Energy Savings"])
                        if measures_data[measure_cateogry][measure]["Typical Energy Savings"] != 0:
                            measures_data[measure_cateogry][measure]["Typical Investments"] = measures_data[measure_cateogry][measure]["Typical Investment per mass"] / measures_data[measure_cateogry][measure]["Typical Energy Savings"]
                        else: 
                            measures_data[measure_cateogry][measure]["Typical Investments"] = 0

                        # if measure != "Seal replacement" or measure != "Low temperature heat recovery for power generation" or measure != "Use of steel slag in kiln (CemStar)": # these are exceptions

                        #     print("This is the category: ", measure_cateogry)
                        #     print("This is measure that it fails on: ", measure)
                            
                            
                        #     if measures_data[measure_cateogry][measure]["Typical Energy Savings"] != 0:
                        #         measures_data[measure_cateogry][measure]["Typical Investments"] = measures_data[measure_cateogry][measure]['Typical Investment per mass'] / measures_data[measure_cateogry][measure]["Typical Energy Savings"]
                        #     else: 
                        #         measures_data[measure_cateogry][measure]["Typical Investments"] = 0
                        
        return measures_data

    all_measures_dict = EE_measure_table(all_measures_dict)

    # Detailed Output Data
    with open(json_folder / "Detailed_Output.json", "r") as f:
        detailed_output_dict = json.load(f)

    # Energy Input Data
    with open(json_folder / "Energy_Input.json", "r") as f:
        energy_input_dict = json.load(f)

    Total_process_electricity = energy_input_dict["Totals"]["Total process electricity"]
    Total_process_fuel = energy_input_dict["Totals"]["Total process fuel"]
    Total_raw_material_and_additive = energy_input_dict["Energy input"]["Homogenization"]["Production Per Process (tonnes/year)"]
    Total_coal_with_generation_and_process_in_mass = energy_input_dict["Energy input"]["Fuel preparation"]["Production Per Process (tonnes/year)"]

    # Production Input Data
    with open(json_folder / "Production_Input.json", "r") as f:
        production_input_dict = json.load(f)

    Total_clinker = production_input_dict["Total clinker production"]
    Total_cement = production_input_dict["Total cement"]

    # Other fields
    grinding_energy = detailed_output_dict["Grinding"]["Your Facility"]
    preblending_energy = detailed_output_dict["Preblending"]["Your Facility"]
    fuel_preparation_energy = detailed_output_dict["Fuel preparation"]["Your Facility"]
    kiln_mechanical_energy = detailed_output_dict['Total kiln mechanical electricity']["Your Facility"]
    kiln_thermal_energy = detailed_output_dict['Total for clinker making fuel']["Your Facility"]
    cement_grinding_energy = detailed_output_dict['Cement grinding']["Your Facility"]

    overall_electricity = Total_process_electricity
    overall_fuel = Total_process_fuel
    detailed_output_dict["overall fuel"] = overall_fuel
    detailed_output_dict["overall electricity"] = overall_electricity


    grinding_energy_initial = detailed_output_dict["Grinding"]["Your Facility"]
    preblending_energy_initial = detailed_output_dict["Preblending"]["Your Facility"]
    fuel_preparation_energy_initial = detailed_output_dict["Fuel preparation"]["Your Facility"]
    kiln_mechanical_energy_initial = detailed_output_dict['Total kiln mechanical electricity']["Your Facility"]
    kiln_thermal_energy_initial = detailed_output_dict['Total for clinker making fuel']["Your Facility"]
    cement_grinding_energy_initial = detailed_output_dict['Cement grinding']["Your Facility"]

    overall_electricity_initial = Total_process_electricity
    overall_fuel_initial = Total_process_fuel

    def EE_measure_table_energy_consumption_shares(measures_data, measure_cateogry, measure, process_energy_use, quantity_of_material_handled):
        if process_energy_use != 0:
            measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"] = measures_data[measure_cateogry][measure]["Typical Energy Savings"] / (process_energy_use / quantity_of_material_handled) # prcess energy use is initial
            #print(measure)
            #print(measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"])
            if measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"] < 1:
                measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"] = measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"]
            else:
                measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"] = 1
        else:
            measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"] = 0
        return measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"]

    def EE_measure_table_total_energy_savings_percentage(measures_data, measure_cateogry, measure):
        measures_data[measure_cateogry][measure]["Total Energy Savings"] = measures_data[measure_cateogry][measure]["Energy Consumption Share of Process"]*measures_data[measure_cateogry][measure]["Potential Application"]
        return measures_data[measure_cateogry][measure]["Total Energy Savings"]

    def EE_measure_table_total_energy_savings(measures_data, measure_cateogry, measure, process_energy_use, quantity_of_material_handled):
        measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"] = measures_data[measure_cateogry][measure]["Total Energy Savings"] * process_energy_use
        
        return measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]

    # EE-RM Preparation
    list_dummy_RM = ["Wash Mills with Closed Circuit Classifier (Wet Process)", 
                "Raw Meal Process Control (Dry process - Vertical Mill)", 
                "High-efficiency classifiers/separators (Dry process)", 
                "Use of Roller Mills (Dry Process)", 
                "Efficient transport systems (Dry process)"]
    for measure in list_dummy_RM:
        if grinding_energy != 0:
            all_measures_dict["EE-RM Preparation"][measure]["Energy Consumption Share of Process"] = all_measures_dict["EE-RM Preparation"][measure]["Typical Energy Savings"] / (grinding_energy_initial / Total_raw_material_and_additive)
        else:
            all_measures_dict["EE-RM Preparation"][measure]["Energy Consumption Share of Process"] = 0
        all_measures_dict["EE-RM Preparation"][measure]["Total Energy Savings - Absolute"] = all_measures_dict["EE-RM Preparation"][measure]["Total Energy Savings"] * grinding_energy
        all_measures_dict["EE-RM Preparation"][measure]["Total Energy Savings"] = all_measures_dict["EE-RM Preparation"][measure]["Energy Consumption Share of Process"]*all_measures_dict["EE-RM Preparation"][measure]["Potential Application"]
        
        # for ordering measures
        if apply_ordering == True:
            if grinding_energy - all_measures_dict["EE-RM Preparation"][measure]["Total Energy Savings - Absolute"] > 0:
                grinding_energy = grinding_energy - all_measures_dict["EE-RM Preparation"][measure]["Total Energy Savings - Absolute"] # the total grinding energy reduces after each measure is applied
                overall_electricity = overall_electricity - all_measures_dict["EE-RM Preparation"][measure]["Total Energy Savings - Absolute"]


    if all_measures_dict["EE-RM Preparation"][ "Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Typical Energy Savings"] / (preblending_energy / Total_raw_material_and_additive) <1:
        all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Energy Consumption Share of Process"] = all_measures_dict["EE-RM Preparation"][ "Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Typical Energy Savings"] / (preblending_energy_initial / Total_raw_material_and_additive)
    else:
        all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Energy Consumption Share of Process"] = 1
    all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Total Energy Savings"] = all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Energy Consumption Share of Process"]*all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Potential Application"]
    all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Total Energy Savings - Absolute"] = all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Total Energy Savings"] * preblending_energy

    # for ordering measures
    if apply_ordering == True:
        if preblending_energy - all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Total Energy Savings - Absolute"] > 0:
            preblending_energy = preblending_energy - all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Total Energy Savings - Absolute"]
            overall_electricity = overall_electricity - all_measures_dict["EE-RM Preparation"]["Raw Meal Blending (Homogenizing) Systems (Dry Process)"]["Total Energy Savings - Absolute"]


    # EE-Fuel Preparation
    all_measures_dict["EE-Fuel Preparation"]["New Efficient Coal Separator for Fuel Preparation"]["Energy Consumption Share of Process"] = EE_measure_table_energy_consumption_shares(all_measures_dict, "EE-Fuel Preparation", "New Efficient Coal Separator for Fuel Preparation", fuel_preparation_energy_initial, Total_coal_with_generation_and_process_in_mass)
    all_measures_dict["EE-Fuel Preparation"]["New Efficient Coal Separator for Fuel Preparation"]["Total Energy Savings"] = EE_measure_table_total_energy_savings_percentage(all_measures_dict, "EE-Fuel Preparation", "New Efficient Coal Separator for Fuel Preparation")
    all_measures_dict["EE-Fuel Preparation"]["New Efficient Coal Separator for Fuel Preparation"]["Total Energy Savings - Absolute"] = EE_measure_table_total_energy_savings(all_measures_dict, "EE-Fuel Preparation", "New Efficient Coal Separator for Fuel Preparation", fuel_preparation_energy, Total_coal_with_generation_and_process_in_mass)
    if apply_ordering == True:
        fuel_preparation_energy = fuel_preparation_energy - all_measures_dict["EE-Fuel Preparation"]["New Efficient Coal Separator for Fuel Preparation"]["Total Energy Savings - Absolute"]
        overall_electricity = overall_electricity - all_measures_dict["EE-Fuel Preparation"]["New Efficient Coal Separator for Fuel Preparation"]["Total Energy Savings - Absolute"]

    all_measures_dict["EE-Fuel Preparation"]["Conversion to efficient roller mills"]["Energy Consumption Share of Process"] = EE_measure_table_energy_consumption_shares(all_measures_dict, "EE-Fuel Preparation", "Conversion to efficient roller mills", fuel_preparation_energy_initial, Total_coal_with_generation_and_process_in_mass)
    all_measures_dict["EE-Fuel Preparation"]["Conversion to efficient roller mills"]["Total Energy Savings"] = EE_measure_table_total_energy_savings_percentage(all_measures_dict, "EE-Fuel Preparation", "Conversion to efficient roller mills")
    all_measures_dict["EE-Fuel Preparation"]["Conversion to efficient roller mills"]["Total Energy Savings - Absolute"] = EE_measure_table_total_energy_savings(all_measures_dict, "EE-Fuel Preparation", "Conversion to efficient roller mills", fuel_preparation_energy, Total_coal_with_generation_and_process_in_mass)
    if apply_ordering == True:
        fuel_preparation_energy = fuel_preparation_energy - all_measures_dict["EE-Fuel Preparation"]["Conversion to efficient roller mills"]["Total Energy Savings - Absolute"]
        overall_electricity = overall_electricity - all_measures_dict["EE-Fuel Preparation"]["Conversion to efficient roller mills"]["Total Energy Savings - Absolute"]

    # EE-Kiln
    list_dummy_kiln = list(all_measures_dict["EE-Kiln"].keys())
    list_dummy_kiln.remove("unit")

    for measure in list_dummy_kiln:
        if all_measures_dict["EE-Kiln"][measure]["Energy Type"] == "Electricity":
            all_measures_dict["EE-Kiln"][measure]["Energy Consumption Share of Process"] = EE_measure_table_energy_consumption_shares(all_measures_dict, "EE-Kiln", measure, kiln_mechanical_energy_initial, Total_clinker)
        else:
            all_measures_dict["EE-Kiln"][measure]["Energy Consumption Share of Process"] = EE_measure_table_energy_consumption_shares(all_measures_dict, "EE-Kiln", measure, kiln_thermal_energy_initial, Total_clinker)

    # Handle exceptions
    list_dummy_kiln_exception = ["Energy management and process control systems",
                                "Seal replacement",
                                "Grate cooler optimization",
                                "Kiln combustion system improvements",
                                "Conversion to reciprocating grate cooler"]

    all_measures_dict["EE-Kiln"]["Energy management and process control systems"]["Energy Consumption Share of Process"] = 0.05
    all_measures_dict["EE-Kiln"]["Seal replacement"]["Energy Consumption Share of Process"] = 0.4/100
    all_measures_dict["EE-Kiln"]["Grate cooler optimization"]["Energy Consumption Share of Process"] = 3.5/100
    all_measures_dict["EE-Kiln"]["Kiln combustion system improvements"]["Energy Consumption Share of Process"] = 0.06
    all_measures_dict["EE-Kiln"]["Conversion to reciprocating grate cooler"]["Energy Consumption Share of Process"] = 0.08

    for measure in list_dummy_kiln_exception:
        all_measures_dict["EE-Kiln"][measure]["Typical Energy Savings"] = all_measures_dict["EE-Kiln"][measure]["Energy Consumption Share of Process"] * kiln_thermal_energy_initial / Total_clinker

    all_measures_dict["EE-Kiln"]["Seal replacement"]["Typical Investments"] = 0.25/29.3
    all_measures_dict["EE-Kiln"]["Low temperature heat recovery for power generation"]["Typical Investments"] = 0.83

    for measure in list_dummy_kiln:
        if all_measures_dict["EE-Kiln"][measure]["Energy Type"] == "Electricity":
            all_measures_dict["EE-Kiln"][measure]["Total Energy Savings"] = EE_measure_table_total_energy_savings_percentage(all_measures_dict, "EE-Kiln", measure)
            all_measures_dict["EE-Kiln"][measure]["Total Energy Savings - Absolute"] = EE_measure_table_total_energy_savings(all_measures_dict, "EE-Kiln", measure, kiln_mechanical_energy, Total_clinker)
            if apply_ordering == True:
                kiln_mechanical_energy = kiln_mechanical_energy - all_measures_dict["EE-Kiln"][measure]["Total Energy Savings - Absolute"]
                overall_electricity = overall_electricity - all_measures_dict["EE-Kiln"][measure]["Total Energy Savings - Absolute"]
        else:
            all_measures_dict["EE-Kiln"][measure]["Total Energy Savings"] = EE_measure_table_total_energy_savings_percentage(all_measures_dict, "EE-Kiln", measure)
            all_measures_dict["EE-Kiln"][measure]["Total Energy Savings - Absolute"] = EE_measure_table_total_energy_savings(all_measures_dict, "EE-Kiln", measure, kiln_thermal_energy, Total_clinker)
            if apply_ordering == True:
                kiln_thermal_energy = kiln_thermal_energy - all_measures_dict["EE-Kiln"][measure]["Total Energy Savings - Absolute"]
                overall_fuel = overall_fuel - all_measures_dict["EE-Kiln"][measure]["Total Energy Savings - Absolute"]

    # EE-Cement Grinding
    list_dummy_cement_grind = list(all_measures_dict["EE-Cement Grinding"].keys())
    list_dummy_cement_grind.remove("unit")

    for measure in list_dummy_cement_grind:
        all_measures_dict["EE-Cement Grinding"][measure]["Energy Consumption Share of Process"] = EE_measure_table_energy_consumption_shares(all_measures_dict, "EE-Cement Grinding", measure, cement_grinding_energy_initial, Total_cement)

    # Handle exception
    all_measures_dict["EE-Cement Grinding"]["Energy management and process control"]["Energy Consumption Share of Process"] = 0.05
    all_measures_dict["EE-Cement Grinding"]["Energy management and process control"]["Typical Energy Savings"] = all_measures_dict["EE-Cement Grinding"]["Energy management and process control"]["Energy Consumption Share of Process"] * cement_grinding_energy_initial / Total_cement

    for measure in list_dummy_cement_grind:
        all_measures_dict["EE-Cement Grinding"][measure]["Total Energy Savings"] = EE_measure_table_total_energy_savings_percentage(all_measures_dict, "EE-Cement Grinding", measure)
        all_measures_dict["EE-Cement Grinding"][measure]["Total Energy Savings - Absolute"] = EE_measure_table_total_energy_savings(all_measures_dict, "EE-Cement Grinding", measure, cement_grinding_energy, Total_cement)
        if apply_ordering == True:
            cement_grinding_energy = cement_grinding_energy - all_measures_dict["EE-Cement Grinding"][measure]["Total Energy Savings - Absolute"]
            overall_electricity = overall_electricity - all_measures_dict["EE-Cement Grinding"][measure]["Total Energy Savings - Absolute"]

    # EE-Product&Feedstock Changes
    list_dummy_product_feedstock_changes = list(all_measures_dict["EE-Product&Feedstock Changes"].keys())
    list_dummy_product_feedstock_changes.remove("unit")
    #list_dummy_product_feedstock_changes.remove("Use of onsite renewable energy") # add separately # already removed amnually

    for measure in list_dummy_product_feedstock_changes:
        all_measures_dict["EE-Product&Feedstock Changes"][measure]["Energy Consumption Share of Process"] = EE_measure_table_energy_consumption_shares(all_measures_dict, "EE-Product&Feedstock Changes", measure, kiln_thermal_energy_initial, Total_clinker)

    # Handle exception
    all_measures_dict["EE-Product&Feedstock Changes"]["Limestone cement"]["Energy Consumption Share of Process"] = 0.05
    all_measures_dict["EE-Product&Feedstock Changes"]["Limestone cement"]["Typical Energy Savings"] = all_measures_dict["EE-Product&Feedstock Changes"]["Limestone cement"]["Energy Consumption Share of Process"] * kiln_thermal_energy_initial / Total_clinker

    all_measures_dict["EE-Product&Feedstock Changes"]["Use of steel slag in kiln (CemStar)"]["Typical Investments"] = (500000/Total_clinker)/all_measures_dict["EE-Product&Feedstock Changes"]["Use of steel slag in kiln (CemStar)"]["Typical Energy Savings"] # it appears that the investment is by installation ($500000 per installation), so the investment per mass is $500000/Total_clinker

    for measure in list_dummy_product_feedstock_changes:
        all_measures_dict["EE-Product&Feedstock Changes"][measure]["Total Energy Savings"] = EE_measure_table_total_energy_savings_percentage(all_measures_dict, "EE-Product&Feedstock Changes", measure)
        all_measures_dict["EE-Product&Feedstock Changes"][measure]["Total Energy Savings - Absolute"] = EE_measure_table_total_energy_savings(all_measures_dict, "EE-Product&Feedstock Changes", measure, kiln_thermal_energy, Total_clinker)
        if apply_ordering == True:    
            kiln_thermal_energy = kiln_thermal_energy - all_measures_dict["EE-Product&Feedstock Changes"][measure]["Total Energy Savings - Absolute"]
            overall_fuel = overall_fuel - all_measures_dict["EE-Product&Feedstock Changes"][measure]["Total Energy Savings - Absolute"]

    # EE-Utility Systems
    list_dummy_utility_motor = ["High efficiency fans", "High efficiency motors", "Variable speed drives in fan systems"]
    for measure in list_dummy_utility_motor:
        all_measures_dict["EE-Utility Systems"][measure]["Energy Consumption Share of Process"] = all_measures_dict["EE-Utility Systems"][measure]["Typical Energy Savings"] / (Total_process_electricity / Total_cement)
        all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings"] = all_measures_dict["EE-Utility Systems"][measure]["Energy Consumption Share of Process"] * all_measures_dict["EE-Utility Systems"][measure]["Potential Application"]
        all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings - Absolute"] = all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings"] * overall_electricity
        all_measures_dict["EE-Utility Systems"][measure]["Typical Investments"] = all_measures_dict["EE-Utility Systems"][measure]['Typical Investment per mass'] / all_measures_dict["EE-Utility Systems"][measure]["Typical Energy Savings"]
        if apply_ordering == True:
            overall_electricity = overall_electricity - all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings - Absolute"]

    list_dummy_utility_compressed_air = ["Reduce leaks",
                                        "Maintenance of compressed air systems",
                                        "Heat recovery for water preheating",
                                        "Reducing inlet air temperature",
                                        "Compressor controls",
                                        "Sizing pipe diameter correctly"]
    compressed_air_energy_intensity = 7.6

    all_measures_dict["EE-Utility Systems"]["Reduce leaks"]["Energy Consumption Share of Process"] = 0.2
    all_measures_dict["EE-Utility Systems"]["Maintenance of compressed air systems"]["Energy Consumption Share of Process"] = 0.15
    all_measures_dict["EE-Utility Systems"]["Heat recovery for water preheating"]["Energy Consumption Share of Process"] = 0.2
    all_measures_dict["EE-Utility Systems"]["Reducing inlet air temperature"]["Energy Consumption Share of Process"] = 0.02
    all_measures_dict["EE-Utility Systems"]["Compressor controls"]["Energy Consumption Share of Process"] = 0.12
    all_measures_dict["EE-Utility Systems"]["Sizing pipe diameter correctly"]["Energy Consumption Share of Process"] = 0.03

    all_measures_dict["EE-Utility Systems"]["Reduce leaks"]["Typical Investments"] = 0.04
    all_measures_dict["EE-Utility Systems"]["Maintenance of compressed air systems"]["Typical Investments"] = 0.06
    all_measures_dict["EE-Utility Systems"]["Heat recovery for water preheating"]["Typical Investments"] = 1/7.5
    all_measures_dict["EE-Utility Systems"]["Reducing inlet air temperature"]["Typical Investments"] = 1.3/7.5
    all_measures_dict["EE-Utility Systems"]["Compressor controls"]["Typical Investments"] = 0.25
    all_measures_dict["EE-Utility Systems"]["Sizing pipe diameter correctly"]["Typical Investments"] = 0.5

    for measure in list_dummy_utility_compressed_air:
        all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings"] = all_measures_dict["EE-Utility Systems"][measure]["Energy Consumption Share of Process"] * all_measures_dict["EE-Utility Systems"][measure]["Potential Application"]
        all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings - Absolute"] = all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings"] * compressed_air_energy_intensity * Total_cement
        all_measures_dict["EE-Utility Systems"][measure]["Typical Energy Savings"] = all_measures_dict["EE-Utility Systems"][measure]["Energy Consumption Share of Process"] * compressed_air_energy_intensity
        if apply_ordering == True:
            overall_electricity = overall_electricity - all_measures_dict["EE-Utility Systems"][measure]["Total Energy Savings - Absolute"]
    
    # Cost and Emission Input Data
    with open(json_folder / "Cost_and_Emission_Input.json", "r") as f:
        cost_and_emissions_dict = json.load(f)

    electricity_price = cost_and_emissions_dict["Cost of electricity in $/kWh"]
    fuel_price = cost_and_emissions_dict["Fuel Price"]
    electricity_emission_intensity = cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000 # convert to kWh # need to add emissions from electricity generation fuel, so do it later # decided to use this variable only for purchased electricity to aid indirect emissions calculations
    fuel_emission_intensity = cost_and_emissions_dict["Fuel Emission Intensity"]


    # Target Input Data
    with open(json_folder / "Target_Input.json", "r") as f:
        target_dict = json.load(f)

    purchased_electricity = target_dict["Purchased Electricity"]

    # Electricity Generation Input
    with open(json_folder / "Electricity_Generation_Input.json", "r") as f:
        electricity_generation_input_dict = json.load(f)

    onsite_RE_electricity_generation = electricity_generation_input_dict["Onsite Renewable Electricity Generation"]
    electricity_fuel_emission_intensity = electricity_generation_input_dict["Electricity Fuel Emission Intensity"]
    onsite_electricity_generation_efficiency = electricity_generation_input_dict["Onsite Electricity Generation Efficiency"]

    # Run this different function to reflect the updates made
    def EE_measure_table_end(measures_data):    
        for measure_cateogry in measures_data.keys():
            for measure in measures_data[measure_cateogry].keys():
                if measure != "unit":
                    
                    measures_data[measure_cateogry][measure]["Total Costs"] = measures_data[measure_cateogry][measure]["Typical Investments"] * measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]
                    
                    if measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"] > 0:                    
                        if measures_data[measure_cateogry][measure]["Energy Type"] == "Electricity":
                            measures_data[measure_cateogry][measure]["Payback Period"] = measures_data[measure_cateogry][measure]["Typical Investments"] / electricity_price
                        else:
                            measures_data[measure_cateogry][measure]["Payback Period"] = measures_data[measure_cateogry][measure]["Typical Investments"] / fuel_price
                    else:
                        measures_data[measure_cateogry][measure]["Payback Period"] = "-"
                    
                    if measures_data[measure_cateogry][measure]["Payback Period"] == 0:
                        measures_data[measure_cateogry][measure]["Payback Period"] = "immediate"      
                    
                    # Add abatement cost
                    if measures_data[measure_cateogry][measure]["Energy Type"] == 'Electricity':
                        if measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"] != 0:
                            measures_data[measure_cateogry][measure]["Abatement cost"] = (measures_data[measure_cateogry][measure]["Total Costs"] + measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]*electricity_price*20)/(measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]*electricity_emission_intensity*20) # 20 is assumed to be the equipment lifetime
                        else:
                            measures_data[measure_cateogry][measure]["Abatement cost"] = 'N/A'
                    elif measures_data[measure_cateogry][measure]["Energy Type"] == 'Fuel':
                        if measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"] != 0:
                            measures_data[measure_cateogry][measure]["Abatement cost"] = (measures_data[measure_cateogry][measure]["Total Costs"] + measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]*fuel_price*20)/(measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]*fuel_emission_intensity*20) # 20 is assumed to be the equipment lifetime
                        else:
                            measures_data[measure_cateogry][measure]["Abatement cost"] = 'N/A'
                    # Add total emission reduction
                    if measures_data[measure_cateogry][measure]["Energy Type"] == 'Electricity':
                        measures_data[measure_cateogry][measure]["Total Emissions Reduction - indirect"] = measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]*electricity_emission_intensity * purchased_electricity / Total_process_electricity #  only accounts for the impacts of purchased electricity
                        measures_data[measure_cateogry][measure]["Total Emissions Reduction - direct"] = measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]*(electricity_fuel_emission_intensity*3.6/onsite_electricity_generation_efficiency)*(1 - ((purchased_electricity+onsite_RE_electricity_generation) / Total_process_electricity)) # emissions from onsite electricity generation
                        measures_data[measure_cateogry][measure]["Total Emissions Reduction"] = measures_data[measure_cateogry][measure]["Total Emissions Reduction - indirect"] + measures_data[measure_cateogry][measure]["Total Emissions Reduction - direct"]
                    elif measures_data[measure_cateogry][measure]["Energy Type"] == 'Fuel':
                        measures_data[measure_cateogry][measure]["Total Emissions Reduction - indirect"] = 0
                        measures_data[measure_cateogry][measure]["Total Emissions Reduction - direct"] = measures_data[measure_cateogry][measure]["Total Energy Savings - Absolute"]*fuel_emission_intensity
                        measures_data[measure_cateogry][measure]["Total Emissions Reduction"] = measures_data[measure_cateogry][measure]["Total Emissions Reduction - indirect"] + measures_data[measure_cateogry][measure]["Total Emissions Reduction - direct"]
            measures_data[measure_cateogry]["unit"]["Abatement cost"] = "$/tCO2"
            measures_data[measure_cateogry]["unit"]["Total Emissions Reduction"] = "tCO2/year"
            measures_data[measure_cateogry]["unit"]["Total Emissions Reduction - direct"] = "tCO2/year"
            measures_data[measure_cateogry]["unit"]["Total Emissions Reduction - indirect"] = "tCO2/year"
            
        return measures_data
    all_measures_dict = EE_measure_table_end(all_measures_dict)

    with open(json_folder / 'all_measures.json', 'w') as f:
        json.dump(all_measures_dict, f, indent=4)

    with pd.ExcelWriter(json_folder / "measures_output_in_excel.xlsx") as writer:
        for sheet in all_measures_dict.keys():
            dummy = pd.DataFrame.from_dict(all_measures_dict[sheet], orient = 'index')
            dummy.to_excel(writer, sheet_name=sheet)
            dummy = dummy.reset_index() # so the measures can also be shown

    # Calculate the energy and emission reduction by measure category
    energy_reduction_by_measure_cat = {}
    emission_reduction_by_measure_cat = {}
    primary_energy_reduction_by_measure_cat = {}
    direct_carbon_reduction_by_measure_cat = {}
    indirect_carbon_reduction_by_measure_cat = {}


    for measure_cateogry in all_measures_dict.keys():
        dummy_final_energy = 0
        dummy_emission = 0
        dummy_primary_energy = 0
        dummy_direct_carbon = 0
        dummy_indirect_carbon = 0
        for measure in all_measures_dict[measure_cateogry].keys():
            if measure != "unit":
                if all_measures_dict[measure_cateogry][measure]['Energy Type'] == 'Electricity':
                    dummy_final_energy += all_measures_dict[measure_cateogry][measure]['Total Energy Savings - Absolute']*3.6
                    dummy_primary_energy += all_measures_dict[measure_cateogry][measure]['Total Energy Savings - Absolute']*3.6/0.305
                    dummy_indirect_carbon += all_measures_dict[measure_cateogry][measure]['Total Emissions Reduction - indirect']
                    dummy_direct_carbon += all_measures_dict[measure_cateogry][measure]['Total Emissions Reduction - direct'] 
                else:
                    dummy_final_energy += all_measures_dict[measure_cateogry][measure]['Total Energy Savings - Absolute']
                    dummy_primary_energy += all_measures_dict[measure_cateogry][measure]['Total Energy Savings - Absolute']
                    dummy_direct_carbon += all_measures_dict[measure_cateogry][measure]['Total Emissions Reduction']
                dummy_emission += all_measures_dict[measure_cateogry][measure]['Total Emissions Reduction']
        energy_reduction_by_measure_cat[measure_cateogry] = dummy_final_energy
        emission_reduction_by_measure_cat[measure_cateogry] = dummy_emission
        primary_energy_reduction_by_measure_cat[measure_cateogry] = dummy_primary_energy
        direct_carbon_reduction_by_measure_cat[measure_cateogry] = dummy_direct_carbon
        indirect_carbon_reduction_by_measure_cat[measure_cateogry] = dummy_indirect_carbon

    EE_measure_direct_emission_reduction = sum(direct_carbon_reduction_by_measure_cat.values()) # there is no process carbon emissions
    EE_measure_indirect_emission_reduction = sum(indirect_carbon_reduction_by_measure_cat.values())

    all_measures_dict["EE_measure_direct_emission_reduction"] = EE_measure_direct_emission_reduction
    all_measures_dict["EE_measure_indirect_emission_reduction"] = EE_measure_indirect_emission_reduction

    with open(json_folder / 'all_measures.json', 'w') as f:
        json.dump(all_measures_dict, f, indent=4)

    with open(json_folder / "energy_reduction_by_measure_cat.json", "w") as f:
        json.dump(energy_reduction_by_measure_cat, f, indent=4)

    with open(json_folder / "emission_reduction_by_measure_cat.json", "w") as f:
        json.dump(emission_reduction_by_measure_cat, f, indent=4)

    with open(json_folder / "primary_energy_reduction_by_measure_cat.json", "w") as f:
        json.dump(primary_energy_reduction_by_measure_cat, f, indent=4)

    with open(json_folder / "direct_carbon_reduction_by_measure_cat.json", "w") as f:
        json.dump(direct_carbon_reduction_by_measure_cat, f, indent=4)

    with open(json_folder / "indirect_carbon_reduction_by_measure_cat.json", "w") as f:
        json.dump(indirect_carbon_reduction_by_measure_cat, f, indent=4)

    with open(json_folder / "Detailed_Output.json", "w") as f:
        json.dump(detailed_output_dict, f, indent=4)

    print("detailed_output_dict keys Page 8 end:")
    print(detailed_output_dict.keys())

    return all_measures_dict


def evaluate_EE_only_popup(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    evaluate_EE_only = "Yes"

    reply = QMessageBox.question(self,
    "Benchmark Choice",
    "Would you like to only benchmark energy efficiency measures?",
    QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes, 
    QMessageBox.StandardButton.Yes
)

    if reply == QMessageBox.StandardButton.Yes:
        evaluate_EE_only = "Yes"
    
    if reply == QMessageBox.StandardButton.No:
        evaluate_EE_only = "No"

    with open(json_folder / "evaluate_EE_only.json", "w") as f:
        json.dump(evaluate_EE_only, f, indent=4)

def Page9_Share_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    # Detailed Output
    with open(json_folder / "Detailed_Output.json", "r") as f:
        detailed_output_dict = json.load(f)

    with open(json_folder / "evaluate_EE_only.json", "r") as f:
        evaluate_EE_only = json.load(f)
    
    # Fuel Switching
    new_fuel_share_dict = {
    "FS-Fuel Switching": {
        "coal": 0.75,
        "coke": 0.0,
        "natural gas": 0.05,
        "biomass": 0.15,
        "municipal wastes": 0.05
        }
    }

    

    if self.ui.coal_input_page9.text() != '':
        new_fuel_share_dict["FS-Fuel Switching"]["coal"] = float(self.ui.coal_input_page9.text())
    if self.ui.coke_input_page9.text() != '':
        new_fuel_share_dict["FS-Fuel Switching"]["coke"] = float(self.ui.coke_input_page9.text())
    if self.ui.natural_gas_input_page9.text() != '':
        new_fuel_share_dict["FS-Fuel Switching"]["natural gas"] = float(self.ui.natural_gas_input_page9.text())
    if self.ui.biomass_input_page9.text() != '':
        new_fuel_share_dict["FS-Fuel Switching"]["biomass"] = float(self.ui.biomass_input_page9.text())
    if self.ui.msw_input_page9.text() != '':
        new_fuel_share_dict["FS-Fuel Switching"]["municipal wastes"] = float(self.ui.msw_input_page9.text())

    fs_emission_reduction = 0

    with open(json_folder / "Cost_and_Emission_Input.json", "r") as f:
        cost_and_emissions_dict = json.load(f)

    fuel_emission_intensity = cost_and_emissions_dict["Fuel Emission Intensity"]

    electricity_emission_intensity = cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000 # convert to kWh # need to add emissions from electricity generation fuel, so do it later # decided to use this variable only for purchased electricity to aid indirect emissions calculations
    coal_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coal']/10**6 # convert to MJ
    coke_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['coke']/10**6
    natural_gas_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['natural gas']/10**6 
    biomass_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['biomass']/10**6 
    msw_emission_intensity = cost_and_emissions_dict["Fuel CO2 intensity (tCO2/TJ)"]['municipal wastes']/10**6 
    carbon_price = cost_and_emissions_dict["Carbon price ($/tCO2)"] 

    new_fuel_emission_intensity = fuel_emission_intensity
    cost_and_emissions_dict["New fuel emission intensity"] = new_fuel_emission_intensity

    # All Measures Input Data
    with open(json_folder / "all_measures.json", 'r') as f:
        all_measures_dict = json.load(f)

    EE_measure_direct_emission_reduction = all_measures_dict["EE_measure_direct_emission_reduction"]
    EE_measure_indirect_emission_reduction = all_measures_dict["EE_measure_indirect_emission_reduction"]

    with open(json_folder / "Benchmarking_Results_Primary.json", "r") as f:
        benchmarking_results_primary_dict = json.load(f)

    Total_carbon_direct = benchmarking_results_primary_dict["Total carbon direct"]
    Total_carbon_indirect = benchmarking_results_primary_dict["Total carbon indirect"]

    with open(json_folder / "energy_reduction_by_measure_cat.json", "r") as f:
        energy_reduction_by_measure_cat = json.load(f)

    with open(json_folder / "emission_reduction_by_measure_cat.json", "r") as f:
        emission_reduction_by_measure_cat = json.load(f)    

    with open(json_folder / "primary_energy_reduction_by_measure_cat.json", "r") as f:
        primary_energy_reduction_by_measure_cat = json.load(f)

    with open(json_folder / "direct_carbon_reduction_by_measure_cat.json", "r") as f:
        direct_carbon_reduction_by_measure_cat = json.load(f)   

    with open(json_folder / "indirect_carbon_reduction_by_measure_cat.json", "r") as f:
        indirect_carbon_reduction_by_measure_cat = json.load(f)

    # Target Input Data
    with open(json_folder / "Target_Input.json", "r") as f:
        target_dict = json.load(f)

    purchased_electricity = target_dict["Purchased Electricity"]

    # Electricity Generation Input
    with open(json_folder / "Electricity_Generation_Input.json", "r") as f:
        electricity_generation_input_dict = json.load(f)

    onsite_RE_electricity_generation = electricity_generation_input_dict["Onsite Renewable Electricity Generation"]
    electricity_fuel_emission_intensity = electricity_generation_input_dict["Electricity Fuel Emission Intensity"]
    onsite_electricity_generation_efficiency = electricity_generation_input_dict["Onsite Electricity Generation Efficiency"]

    # Energy Input
    with open(json_folder / "Energy_Input.json", "r") as f:
        energy_input_dict = json.load(f)

    Total_process_electricity = energy_input_dict["Totals"]["Total process electricity"]

    if evaluate_EE_only == "Yes":
        print('FS measures are not evaluated') # where is the partial application?
    else:
        
        new_fuel_emission_intensity = coal_emission_intensity * new_fuel_share_dict["FS-Fuel Switching"]["coal"] + coke_emission_intensity * new_fuel_share_dict["FS-Fuel Switching"]["coke"] + natural_gas_emission_intensity * new_fuel_share_dict["FS-Fuel Switching"]["natural gas"] + biomass_emission_intensity * new_fuel_share_dict["FS-Fuel Switching"]["biomass"] + msw_emission_intensity * new_fuel_share_dict["FS-Fuel Switching"]["municipal wastes"]
        cost_and_emissions_dict["New fuel emission intensity"] = new_fuel_emission_intensity
        direct_emission_before_fs = Total_carbon_direct - EE_measure_direct_emission_reduction
        fs_emission_reduction = direct_emission_before_fs * (1 - new_fuel_emission_intensity/fuel_emission_intensity)
        direct_carbon_reduction_by_measure_cat["FS-Fuel Switch"] = fs_emission_reduction
        emission_reduction_by_measure_cat["FS-Fuel Switch"] = fs_emission_reduction
        
    FS_measure_direct_emission_reduction = fs_emission_reduction
    new_fuel_share_dict["FS measure direct emission reduction"] = FS_measure_direct_emission_reduction

    with open(json_folder / "new_fuel_share.json", 'w') as f:
        json.dump(new_fuel_share_dict, f, indent=4)

    with open(json_folder / "Cost_and_Emission_Input.json", "w") as f:
        json.dump(cost_and_emissions_dict, f, indent=4)

    ## Purchase/generate renewable energy
    new_re_share_dict = {
    "RE-Renewable Energy": {
        "share of electricity from purchased or self-generated renewable energy": 0.75
        }
    }

    if self.ui.share_electricity_input_page9.text() != '':
        new_re_share_dict["RE-Renewable Energy"]["share of electricity from purchased or self-generated renewable energy"] = float(self.ui.share_electricity_input_page9.text())

    re_emission_reduction_indirect = 0
    re_emission_reduction_direct = 0

    if evaluate_EE_only == "Yes":
        print('RE measures are not evaluated')
    else:
        indirect_emission_before_re = Total_carbon_indirect - EE_measure_indirect_emission_reduction
        
        re_emission_reduction_indirect = indirect_emission_before_re * new_re_share_dict["RE-Renewable Energy"]["share of electricity from purchased or self-generated renewable energy"]
        re_emission_reduction_direct = re_emission_reduction_indirect*((Total_process_electricity-purchased_electricity-onsite_RE_electricity_generation) / purchased_electricity)*((electricity_fuel_emission_intensity*3.6/onsite_electricity_generation_efficiency)/electricity_emission_intensity)
        indirect_carbon_reduction_by_measure_cat["RE-Renewable Energy"] = re_emission_reduction_indirect
        direct_carbon_reduction_by_measure_cat["RE-Renewable Energy"] = re_emission_reduction_direct
        emission_reduction_by_measure_cat["RE-Renewable Energy"] = re_emission_reduction_indirect + re_emission_reduction_direct

    RE_measure_direct_emission_reduction = re_emission_reduction_direct
    new_re_share_dict["RE measure direct emission reduction"] = RE_measure_direct_emission_reduction

    with open(json_folder / "new_re_share.json", 'w') as f:
        json.dump(new_re_share_dict, f, indent=4)

    

    return new_fuel_share_dict, new_re_share_dict 


def Page10_AllDTMeasures_Default_Update_Fields(self):
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    json_folder = data_dir / "Saved Progress"

    def jload(p):
        with open(p, "r") as f:
            return json.load(f)

    detailed_output_dict = jload(json_folder / "Detailed_Output.json")
    benchmarking_results_primary_dict = jload(json_folder / "Benchmarking_Results_Primary.json")
    production_input_dict = jload(json_folder / "Production_Input.json")
    energy_input_dict = jload(json_folder / "Energy_Input.json")
    cost_and_emissions_dict = jload(json_folder / "Cost_and_Emission_Input.json")
    energy_reduction_by_measure_cat = jload(json_folder / "energy_reduction_by_measure_cat.json")
    emission_reduction_by_measure_cat = jload(json_folder / "emission_reduction_by_measure_cat.json")
    primary_energy_reduction_by_measure_cat = jload(json_folder / "primary_energy_reduction_by_measure_cat.json")
    direct_carbon_reduction_by_measure_cat = jload(json_folder / "direct_carbon_reduction_by_measure_cat.json")
    indirect_carbon_reduction_by_measure_cat = jload(json_folder / "indirect_carbon_reduction_by_measure_cat.json")
    target_dict = jload(json_folder / "Target_Input.json")
    electricity_generation_input_dict = jload(json_folder / "Electricity_Generation_Input.json")
    all_measures_dict = jload(json_folder / "all_measures.json")
    evaluate_EE_only = jload(json_folder / "evaluate_EE_only.json")
    new_re_share_dict = jload(json_folder / "new_re_share.json")
    new_fuel_share_dict = jload(json_folder / "new_fuel_share.json")

    all_DT_measures_dict = {
        "DT-SCM and Fillers": {
            "unit": {
                "Do you want to apply this measure?": "NaN",
                "Potential Application": "(%)",
                "Energy Impacts (electricity)": "kWh/tonne cement",
                "Energy Impacts (thermal)": "MJ/tonne cement",
                "CO2 impacts (indirect)": "tCO2/tonne cement",
                "CO2 impacts (direct energy)": "tCO2/tonne cement",
                "CO2 impacts (direct process)": "tCO2/tonne cement",
                "Typical Investments": "USD/tonne cement-year",
                "Total Investments": "USD",
                "Total Emissions Reduction": "tCO2/year",
                "Equipment Lifetime": "Years",
                "Abatement cost": "$/tCO2",
                "Payback Period with carbon price": "years",
                "Energy Impacts (thermal) - initial": "MJ/tonne cement",
                "Energy Impacts (electricity) - initial": "kWh/tonne cement",
                "CO2 impacts (direct process) - initial": "tCO2/tonne cement"
            },
            "Use of granulated last furnace slag": {
                "Do you want to apply this measure?": "Yes (100%)",
                "Potential Application": 1.0,
                "Energy Impacts (electricity)": 19,
                "Energy Impacts (thermal)": -2514,
                "CO2 impacts (indirect)": 0.003350167468424886,
                "CO2 impacts (direct energy)": -0.1663769207013374,
                "CO2 impacts (direct process)": -0.3962036,
                "Typical Investments": 5.205479452054794,
                "Total Investments": 650684.9315068492,
                "Total Emissions Reduction": 69903.79415411406,
                "Equipment Lifetime": 20,
                "Abatement cost": -133.2330158904135,
                "Payback Period with carbon price": -0.0818682545688344,
                "Energy Impacts (thermal) - initial": -2514,
                "Energy Impacts (electricity) - initial": 19,
                "CO2 impacts (direct process) - initial": -0.3962036
            },
            "Use of fly ash": {
                "Do you want to apply this measure?": "No (0%)",
                "Potential Application": 0.0,
                "Energy Impacts (electricity)": 8,
                "Energy Impacts (thermal)": -1000,
                "CO2 impacts (indirect)": 0.0,
                "CO2 impacts (direct energy)": 0.0,
                "CO2 impacts (direct process)": -0.15739999999999998,
                "Typical Investments": 6.2465753424657535,
                "Total Investments": 0.0,
                "Total Emissions Reduction": -0.0,
                "Equipment Lifetime": 20,
                "Abatement cost": "error",
                "Payback Period with carbon price": "N/A",
                "Energy Impacts (thermal) - initial": -1000,
                "Energy Impacts (electricity) - initial": 8,
                "CO2 impacts (direct process) - initial": -0.15739999999999998
            },
            "Use of calcined clay": {
                "Do you want to apply this measure?": "No (0%)",
                "Potential Application": 0.0,
                "Energy Impacts (electricity)": 15,
                "Energy Impacts (thermal)": -1500,
                "CO2 impacts (indirect)": 0.0,
                "CO2 impacts (direct energy)": 0.0,
                "CO2 impacts (direct process)": -0.2361,
                "Typical Investments": 6.2465753424657535,
                "Total Investments": 0.0,
                "Total Emissions Reduction": -0.0,
                "Equipment Lifetime": 20,
                "Abatement cost": "error",
                "Payback Period with carbon price": "N/A",
                "Energy Impacts (thermal) - initial": -1500,
                "Energy Impacts (electricity) - initial": 15,
                "CO2 impacts (direct process) - initial": -0.2361
            },
            "Use of recycled concrete fines as filler": {
                "Do you want to apply this measure?": "No (0%)",
                "Potential Application": 0.0,
                "Energy Impacts (electricity)": 15,
                "Energy Impacts (thermal)": -550,
                "CO2 impacts (indirect)": 0.0,
                "CO2 impacts (direct energy)": 0.0,
                "CO2 impacts (direct process)": -0.15406999999999998,
                "Typical Investments": 10.3,
                "Total Investments": 0.0,
                "Total Emissions Reduction": -0.0,
                "Equipment Lifetime": 20,
                "Abatement cost": "error",
                "Payback Period with carbon price": "N/A",
                "Energy Impacts (thermal) - initial": -550,
                "Energy Impacts (electricity) - initial": 15,
                "CO2 impacts (direct process) - initial": -0.15406999999999998
            },
            "Use of limestone as fillers": {
                "Do you want to apply this measure?": "Yes (100%)",
                "Potential Application": 1.0,
                "Energy Impacts (electricity)": 0,
                "Energy Impacts (thermal)": -144.72,
                "CO2 impacts (indirect)": 0.0,
                "CO2 impacts (direct energy)": -0.0024181763912832304,
                "CO2 impacts (direct process)": -0.035558928000000004,
                "Typical Investments": 0,
                "Total Investments": 0.0,
                "Total Emissions Reduction": 405.2447779104041,
                "Equipment Lifetime": 20,
                "Abatement cost": -342.706144575437,
                "Payback Period with carbon price": "immediate",
                "Energy Impacts (thermal) - initial": -144.72,
                "Energy Impacts (electricity) - initial": 0,
                "CO2 impacts (direct process) - initial": -0.035558928000000004
            }
        },
        "DT-Alternative Cements": {
            "unit": {
                "Do you want to apply this measure?": "NaN",
                "Potential Application": "(%)",
                "Energy Impacts (electricity)": "kWh/tonne cement",
                "Energy Impacts (thermal)": "MJ/tonne cement",
                "CO2 impacts (indirect)": "tCO2/tonne cement",
                "CO2 impacts (direct energy)": "tCO2/tonne cement",
                "CO2 impacts (direct process)": "tCO2/tonne cement",
                "Typical Investments": "USD/tonne cement-year",
                "Total Investments": "USD",
                "Total Emissions Reduction": "tCO2/year",
                "Equipment Lifetime": "Years",
                "Abatement cost": "$/tCO2",
                "Payback Period with carbon price": "years",
                "Energy Impacts (thermal) - initial": "MJ/tonne cement",
                "Energy Impacts (electricity) - initial": "kWh/tonne cement",
                "CO2 impacts (direct process) - initial": "tCO2/tonne cement"
            },
            "Use of belite cement": {
                "Do you want to apply this measure?": "Yes (100%)",
                "Potential Application": 1.0,
                "Energy Impacts (electricity)": 0,
                "Energy Impacts (thermal)": -216,
                "CO2 impacts (indirect)": 0.0,
                "CO2 impacts (direct energy)": -0.003453764297870089,
                "CO2 impacts (direct process)": 0,
                "Typical Investments": 0,
                "Total Investments": 0.0,
                "Total Emissions Reduction": 431.72053723376115,
                "Equipment Lifetime": 20,
                "Abatement cost": -459.4532506317482,
                "Payback Period with carbon price": "immediate",
                "Energy Impacts (thermal) - initial": -216,
                "Energy Impacts (electricity) - initial": 0,
                "CO2 impacts (direct process) - initial": 0
            },
            "Use of CSA cement": {
                "Do you want to apply this measure?": "No (0%)",
                "Potential Application": 0.0,
                "Energy Impacts (electricity)": -26,
                "Energy Impacts (thermal)": 0,
                "CO2 impacts (indirect)": -0.0,
                "CO2 impacts (direct energy)": 0.0,
                "CO2 impacts (direct process)": 0,
                "Typical Investments": 0,
                "Total Investments": 0.0,
                "Total Emissions Reduction": -0.0,
                "Equipment Lifetime": 20,
                "Abatement cost": "error",
                "Payback Period with carbon price": "N/A",
                "Energy Impacts (thermal) - initial": 0,
                "Energy Impacts (electricity) - initial": -26,
                "CO2 impacts (direct process) - initial": 0
            }
        },
        "DT-CCUS": {
            "unit": {
                "Do you want to apply this measure?": "NaN",
                "Potential Application": "(%)",
                "Energy Impacts (electricity)": "kWh/tonne cement",
                "Energy Impacts (thermal)": "MJ/tonne cement",
                "CO2 impacts (indirect)": "tCO2/tonne cement",
                "CO2 impacts (direct energy)": "tCO2/tonne cement",
                "CO2 impacts (direct process)": "tCO2/tonne cement",
                "Typical Investments": "USD/tonne cement-year",
                "Total Investments": "USD",
                "Total Emissions Reduction": "tCO2/year",
                "Equipment Lifetime": "Years",
                "Abatement cost": "$/tCO2",
                "Payback Period with carbon price": "years",
                "Energy Impacts (thermal) - initial": "MJ/tonne cement",
                "Energy Impacts (electricity) - initial": "kWh/tonne cement",
                "CO2 impacts (direct process) - initial": "tCO2/tonne cement"
            },
            "Absorption": {
                "Do you want to apply this measure?": "Yes (100%)",
                "Potential Application": 1.0,
                "Energy Impacts (electricity)": 129,
                "Energy Impacts (thermal)": 3500,
                "CO2 impacts (indirect)": 0.025583134916478175,
                "CO2 impacts (direct energy)": 0.05588307418558598,
                "CO2 impacts (direct process)": 0,
                "Typical Investments": 143.15068493150685,
                "Total Investments": 17893835.616438355,
                "Total Emissions Reduction": -10183.276137758021,
                "Equipment Lifetime": 20,
                "Abatement cost": "error",
                "Payback Period with carbon price": 3.8866766028007858,
                "Energy Impacts (thermal) - initial": 3500,
                "Energy Impacts (electricity) - initial": 129,
                "CO2 impacts (direct process) - initial": 0
            },
            "Calcium looping": {
                "Do you want to apply this measure?": "No (0%)",
                "Potential Application": 0.0,
                "Energy Impacts (electricity)": 50,
                "Energy Impacts (thermal)": 2450,
                "CO2 impacts (indirect)": 0.0,
                "CO2 impacts (direct energy)": 0.0,
                "CO2 impacts (direct process)": 0,
                "Typical Investments": 257.67123287671234,
                "Total Investments": 0.0,
                "Total Emissions Reduction": -0.0,
                "Equipment Lifetime": 20,
                "Abatement cost": "error",
                "Payback Period with carbon price": "N/A",
                "Energy Impacts (thermal) - initial": 2450,
                "Energy Impacts (electricity) - initial": 50,
                "CO2 impacts (direct process) - initial": 0
            }
        }
    }

    page10_all_measures_map = {
    "DT-SCM and Fillers": {
        "Use of granulated last furnace slag": {
            "comboBox": "page_10_comboBox",
            "input": "page_10_input",
        },
        "Use of fly ash": {
            "comboBox": "page_10_comboBox_2",
            "input": "page_10_input_2",
        },
        "Use of calcined clay": {
            "comboBox": "page_10_comboBox_3",
            "input": "page_10_input_3",
        },
        "Use of recycled concrete fines as filler": {
            "comboBox": "page_10_comboBox_4",
            "input": "page_10_input_4",
        },
        "Use of limestone as fillers": {
            "comboBox": "page_10_comboBox_5",
            "input": "page_10_input_5",
        },
    },
    "DT-Alternative Cements": {
        "Use of belite cement": {
            "comboBox": "page_10_comboBox_6",
            "input": "page_10_input_6",
        },
        "Use of CSA cement": {
            "comboBox": "page_10_comboBox_7",
            "input": "page_10_input_7",
        },
    },
    "DT-CCUS": {
        "Absorption": {
            "comboBox": "page_10_comboBox_8",
            "input": "page_10_input_8",
        },
        "Calcium looping": {
            "comboBox": "page_10_comboBox_9",
            "input": "page_10_input_9",
        },
        }
    }

    for unit, measures in page10_all_measures_map.items():
        for measure, widgets in measures.items():

            combo = getattr(self.ui, widgets["comboBox"])
            choice = combo.currentText()

            input_widget = getattr(self.ui, widgets["input"])
            input_text = input_widget.text().strip()

            # default to 0 if empty, otherwise convert to float
            input_value = float(input_text) if input_text else 0

            if choice in ["Yes (100%)", "No (0%)"]:
                all_DT_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_DT_measures_dict[unit][measure]["Potential Application"] = 1 if "Yes" in choice else 0
            elif choice in ["Yes, Partially"]:
                all_DT_measures_dict[unit][measure]["Do you want to apply this measure?"] = choice
                all_DT_measures_dict[unit][measure]["Potential Application"] = input_value

            print("this is what is saved in the dict", all_DT_measures_dict[unit][measure]["Do you want to apply this measure?"])
            print("this is what is saved in the dict", all_DT_measures_dict[unit][measure]["Potential Application"])

    with open(json_folder / "all_DT_measures.json", "w") as f:
        json.dump(all_DT_measures_dict, f)

    print("page 10 all done")

    # Benchmarking Results Primary
    Total_process_carbon = benchmarking_results_primary_dict["Total process carbon"]
    Total_carbon_all = benchmarking_results_primary_dict["Total carbon all"]
    Total_carbon_direct = benchmarking_results_primary_dict["Total carbon direct"]
    Total_carbon_indirect = benchmarking_results_primary_dict["Total carbon indirect"]
    Total_process_carbon = benchmarking_results_primary_dict["Total process carbon"]

    Target_carbon_indirect = benchmarking_results_primary_dict["Target carbon indirect"]
    Target_carbon_direct = benchmarking_results_primary_dict["Target carbon direct"]
    Target_carbon_all = benchmarking_results_primary_dict["Target carbon all"]

    IBP_carbon_indirect = benchmarking_results_primary_dict["IBP carbon indirect"]
    IBP_carbon_direct = benchmarking_results_primary_dict["IBP carbon direct"]
    IBP_carbon_all = benchmarking_results_primary_dict["IBP carbon all"]
    IBP_with_different_fuel_carbon_direct = benchmarking_results_primary_dict["IBP with different fuel carbon direct"]

    # Production Input
    Total_cement = production_input_dict["Total cement"]
    Total_clinker = production_input_dict["Total clinker production"]

    # Energy Input
    Total_process_fuel = energy_input_dict["Totals"]["Total process fuel"]
    Total_process_electricity = energy_input_dict["Totals"]["Total process electricity"]

    # Cost and Emission Input Data
    electricity_price = cost_and_emissions_dict["Cost of electricity in $/kWh"]
    fuel_price = cost_and_emissions_dict["Fuel Price"]
    electricity_emission_intensity = cost_and_emissions_dict["Grid CO2 emission intensity (tCO2/MWh)"]/1000
    fuel_emission_intensity = cost_and_emissions_dict["Fuel Emission Intensity"]

    # Target Input Data
    purchased_electricity = target_dict["Purchased Electricity"]
    Target_final = target_dict["Target Final"]

    # Electricity Generation Input
    onsite_RE_electricity_generation = electricity_generation_input_dict["Onsite Renewable Electricity Generation"]
    electricity_fuel_emission_intensity = electricity_generation_input_dict["Electricity Fuel Emission Intensity"]
    onsite_electricity_generation_efficiency = electricity_generation_input_dict["Onsite Electricity Generation Efficiency"]

    # Energy Input again (we already have energy_input_dict)
    Total_process_electricity = energy_input_dict["Totals"]["Total process electricity"]
    Total_final_energy = energy_input_dict["Total Final Energy Consumption (MJ/year)"]
    Total_primary_energy = energy_input_dict["Total Primary Energy Consumption (MJ/year)"]
    Total_process_fuel = energy_input_dict["Totals"]["Total process fuel"]

    # All Measures
    print("all_measures_dict keys for Page 10 end:")
    EE_measure_direct_emission_reduction = all_measures_dict["EE_measure_direct_emission_reduction"]
    EE_measure_indirect_emission_reduction = all_measures_dict["EE_measure_indirect_emission_reduction"]

    # Cost and Emission
    new_fuel_emission_intensity = cost_and_emissions_dict["New fuel emission intensity"]
    carbon_price = cost_and_emissions_dict["Carbon price ($/tCO2)"] 

    # new_re_share/new_fuel_share already loaded
    FS_measure_direct_emission_reduction = new_fuel_share_dict["FS measure direct emission reduction"]
    RE_measure_direct_emission_reduction = new_re_share_dict["RE measure direct emission reduction"]

    # Detailed Output
    overall_fuel = detailed_output_dict["overall fuel"]
    overall_electricity = detailed_output_dict["overall electricity"]

    IBP_total_final_energy = detailed_output_dict["IBP total final energy"]
    IBP_total_primary_energy = detailed_output_dict["IBP total primary energy"]
    IBP_total_fuel = detailed_output_dict["IBP total fuel"]
    IBP_total_electricity = detailed_output_dict["IBP total electricity"]

    overall_process_carbon = Total_process_carbon

    def DT_measure_table(measures_data): 
        nonlocal overall_fuel  
        nonlocal overall_electricity
        nonlocal overall_process_carbon
        for measure_cateogry in measures_data.keys():
            for measure in measures_data[measure_cateogry].keys():
                measures_data[measure_cateogry][measure]["Energy Impacts (thermal) - initial"] = measures_data[measure_cateogry][measure]["Energy Impacts (thermal)"]
                measures_data[measure_cateogry][measure]["Energy Impacts (electricity) - initial"] = measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"]
                measures_data[measure_cateogry][measure]["CO2 impacts (direct process) - initial"] = measures_data[measure_cateogry][measure]["CO2 impacts (direct process)"]
                if measure != "unit":
                    if measures_data[measure_cateogry][measure]["Do you want to apply this measure?"] == "Yes (100%)":
                        measures_data[measure_cateogry][measure]["Potential Application"] = 1
                    elif measures_data[measure_cateogry][measure]["Do you want to apply this measure?"] == "No (0%)":
                        measures_data[measure_cateogry][measure]["Potential Application"] = 0
                    else:
                        measures_data[measure_cateogry][measure]["Potential Application"] = measures_data[measure_cateogry][measure]["Potential Application"]
                    
                    measures_data[measure_cateogry][measure]["Energy Impacts (thermal)"] = measures_data[measure_cateogry][measure]["Energy Impacts (thermal)"] * (overall_fuel/Total_process_fuel) * measures_data[measure_cateogry][measure]["Potential Application"]
                    measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"] = measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"] * (overall_electricity/Total_process_electricity) * measures_data[measure_cateogry][measure]["Potential Application"]
                    
                    # set remaining energy use or emissions to zero in case it is already reduced to below zero in previous steps
                    if overall_fuel < 0:
                        overall_fuel = 0
                    if overall_electricity < 0:
                        overall_fuel = 0 
                    if overall_process_carbon < 0:
                        overall_process_carbon = 0
                    
                    overall_fuel = overall_fuel + measures_data[measure_cateogry][measure]["Energy Impacts (thermal)"] * Total_cement 
                    overall_electricity = overall_electricity + measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"] * Total_cement 
                    
                    measures_data[measure_cateogry][measure]["CO2 impacts (indirect)"] = measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"]*electricity_emission_intensity * (purchased_electricity/Total_process_electricity) * new_re_share_dict["RE-Renewable Energy"]["share of electricity from purchased or self-generated renewable energy"]
                    measures_data[measure_cateogry][measure]["CO2 impacts (direct energy)"] = measures_data[measure_cateogry][measure]["Energy Impacts (thermal)"]*new_fuel_emission_intensity + measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"]*(electricity_fuel_emission_intensity*3.6/onsite_electricity_generation_efficiency)*(1-((purchased_electricity+onsite_RE_electricity_generation)/Total_process_electricity)) # changed after fossil switch # added emissions from onsite generation
                    
                    measures_data[measure_cateogry][measure]["CO2 impacts (direct process)"] = measures_data[measure_cateogry][measure]["CO2 impacts (direct process)"] * (overall_process_carbon/Total_process_carbon) * measures_data[measure_cateogry][measure]["Potential Application"] # I set CCUS's process emissions at zero, and I will handle separately
                    overall_process_carbon = overall_process_carbon + measures_data[measure_cateogry][measure]["CO2 impacts (direct process)"] * Total_cement
                    
                    measures_data[measure_cateogry][measure]['Total Investments'] = measures_data[measure_cateogry][measure]['Typical Investments']*Total_cement*measures_data[measure_cateogry][measure]["Potential Application"]
                    measures_data[measure_cateogry][measure]['Total Emissions Reduction'] = -(measures_data[measure_cateogry][measure]["CO2 impacts (indirect)"]+measures_data[measure_cateogry][measure]["CO2 impacts (direct energy)"]+measures_data[measure_cateogry][measure]["CO2 impacts (direct process)"])*Total_cement
                
                    if measures_data[measure_cateogry][measure]["Total Emissions Reduction"] > 0:
                        measures_data[measure_cateogry][measure]["Abatement cost"] = (measures_data[measure_cateogry][measure]['Typical Investments'] + (measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"]*electricity_price + measures_data[measure_cateogry][measure]["Energy Impacts (thermal)"]*fuel_price)*measures_data[measure_cateogry][measure]["Equipment Lifetime"])*Total_cement/(measures_data[measure_cateogry][measure]["Total Emissions Reduction"]*measures_data[measure_cateogry][measure]["Equipment Lifetime"])
                    else:
                        measures_data[measure_cateogry][measure]["Abatement cost"] = "error"
                    
                    if measures_data[measure_cateogry][measure]["Potential Application"] > 0:
                        if measures_data[measure_cateogry][measure]['Total Investments'] <= 0:
                            measures_data[measure_cateogry][measure]["Payback Period with carbon price"] = "immediate"
                        else: 
                            measures_data[measure_cateogry][measure]["Payback Period with carbon price"] = measures_data[measure_cateogry][measure]['Total Investments'] / (measures_data[measure_cateogry][measure]["Total Emissions Reduction"]*carbon_price + (measures_data[measure_cateogry][measure]["Energy Impacts (electricity)"]*electricity_price + measures_data[measure_cateogry][measure]["Energy Impacts (thermal)"]*fuel_price)*Total_cement)
                    else:
                        measures_data[measure_cateogry][measure]["Payback Period with carbon price"] = "N/A"
                    
        return measures_data
    
    all_DT_measures_dict = DT_measure_table(all_DT_measures_dict)

    if evaluate_EE_only != "Yes":
        with pd.ExcelWriter(json_folder / "measures_DT_output_in_excel.xlsx") as writer:
            for sheet in all_DT_measures_dict.keys():
                dummy = pd.DataFrame.from_dict(all_DT_measures_dict[sheet], orient = 'index')
                dummy.to_excel(writer, sheet_name=sheet)        
                dummy = dummy.reset_index()

    # Calculate the energy and emission reduction by measure category
    CCUS_emission_reduction_percentage = 0
    for measure in all_DT_measures_dict["DT-CCUS"].keys():
        if measure != 'unit':
            CCUS_emission_reduction_percentage += all_DT_measures_dict["DT-CCUS"][measure]["Potential Application"]

    if evaluate_EE_only == "Yes":
        print('DT measures are not evaluated')
    else:
        DT_measure_direct_emission_reduction = 0    
        for measure_cateogry in all_DT_measures_dict.keys():
            dummy_final_energy = 0
            dummy_emission = 0
            dummy_primary_energy = 0
            dummy_direct_carbon = 0
            dummy_indirect_carbon = 0
            for measure in all_DT_measures_dict[measure_cateogry].keys():
                if measure != "unit":
                    dummy_final_energy += -(all_DT_measures_dict[measure_cateogry][measure]['Energy Impacts (electricity)']*3.6 + all_DT_measures_dict[measure_cateogry][measure]['Energy Impacts (thermal)'])*Total_cement
                    dummy_primary_energy += -(all_DT_measures_dict[measure_cateogry][measure]['Energy Impacts (electricity)']*3.6/0.305 + all_DT_measures_dict[measure_cateogry][measure]['Energy Impacts (thermal)'])*Total_cement
                    dummy_emission += all_DT_measures_dict[measure_cateogry][measure]['Total Emissions Reduction']
                    dummy_direct_carbon += -(all_DT_measures_dict[measure_cateogry][measure]['CO2 impacts (direct energy)']*all_DT_measures_dict[measure_cateogry][measure]['Potential Application']*Total_cement)
                    dummy_indirect_carbon += -(all_DT_measures_dict[measure_cateogry][measure]['CO2 impacts (indirect)']*all_DT_measures_dict[measure_cateogry][measure]['Potential Application']*Total_cement)
                    
                    DT_measure_direct_emission_reduction += -((all_DT_measures_dict[measure_cateogry][measure]['CO2 impacts (direct energy)']+all_DT_measures_dict[measure_cateogry][measure]['CO2 impacts (direct process)'])*all_DT_measures_dict[measure_cateogry][measure]['Potential Application']*Total_cement)          
            energy_reduction_by_measure_cat[measure_cateogry] = dummy_final_energy
            emission_reduction_by_measure_cat[measure_cateogry] = dummy_emission
            primary_energy_reduction_by_measure_cat[measure_cateogry] = dummy_primary_energy
            direct_carbon_reduction_by_measure_cat[measure_cateogry] = dummy_direct_carbon
            indirect_carbon_reduction_by_measure_cat[measure_cateogry] = dummy_indirect_carbon

        # Handle CCUS
        emission_reduction_by_measure_cat["DT-CCUS"] = direct_carbon_reduction_by_measure_cat["DT-CCUS"] + ((Total_carbon_all-Total_carbon_indirect)-EE_measure_direct_emission_reduction-DT_measure_direct_emission_reduction-FS_measure_direct_emission_reduction-RE_measure_direct_emission_reduction)*(CCUS_emission_reduction_percentage)

    exempt_keys_all_measures_dict = ['EE_measure_direct_emission_reduction', 'EE_measure_indirect_emission_reduction']

    abatement_cost = {}
    for measure_cateogry in all_measures_dict.keys():
        if measure_cateogry not in exempt_keys_all_measures_dict:
            for measure in all_measures_dict[measure_cateogry].keys():
                if measure != 'unit': 
                    if all_measures_dict[measure_cateogry][measure]["Abatement cost"] != 'N/A' and all_measures_dict[measure_cateogry][measure]["Abatement cost"] < 5000:
                        abatement_cost[measure] = {}
                        abatement_cost[measure]['Abatement Cost'] = all_measures_dict[measure_cateogry][measure]["Abatement cost"]
                        abatement_cost[measure]["Total Emissions Reduction"] = all_measures_dict[measure_cateogry][measure]["Total Emissions Reduction"]
                        abatement_cost[measure]["Type"] = "EE"
    
    for measure_cateogry in all_DT_measures_dict.keys():
        for measure in all_DT_measures_dict[measure_cateogry].keys():
            if measure != 'unit': 
                if all_DT_measures_dict[measure_cateogry][measure]["Abatement cost"] != 'error' and all_DT_measures_dict[measure_cateogry][measure]["Abatement cost"] <5000:
                    abatement_cost[measure] = {}
                    abatement_cost[measure]['Abatement Cost'] = all_DT_measures_dict[measure_cateogry][measure]["Abatement cost"] 
                    abatement_cost[measure]["Total Emissions Reduction"] = all_DT_measures_dict[measure_cateogry][measure]["Total Emissions Reduction"]
                    abatement_cost[measure]["Type"] = "DT"

    df_abatement_cost = pd.DataFrame.from_dict(abatement_cost)
    df_abatement_cost = df_abatement_cost.T
    df_abatement_cost = df_abatement_cost.reset_index()

    plt.figure(figsize=(12, 8))

    df_abatement_cost = df_abatement_cost.sort_values(by='Abatement Cost', ascending=True)

    measures = list(df_abatement_cost['index'])
    abatement_costs = list(df_abatement_cost['Abatement Cost'])
    emissions = list(df_abatement_cost["Total Emissions Reduction"])
    sources = list(df_abatement_cost['Type'])

    cumulative_width = 0
    positions = []
    for emission in emissions:
        positions.append(cumulative_width)
        cumulative_width += emission

    color_map = {
        'EE': 'red',
        'DT': 'blue',
        }

    colors = [color_map[source] for source in sources]

    for i, (pos, measure, cost, emission, color) in enumerate(zip(positions, measures, abatement_costs, emissions, colors)):
        plt.bar(pos, cost, width=emission, color=color, edgecolor='black', align='edge')

    plt.ylabel('Abatement Cost', fontsize=18)
    plt.xlabel('Measures / Annual Total Emission Reduction (tCO2)', fontsize=18)
    plt.title('Abatement Cost Curve', fontsize=18)

    plt.grid()
    plt.savefig(data_dir / "Graphs/abatement cost.png")
    plt.close()
    # plt.show()

    # Plot waterfall chart
    # Final Energy
    list_of_measure_categories = list(energy_reduction_by_measure_cat.keys())
    list_of_energy_reduction = []

    for measure_cateogry in energy_reduction_by_measure_cat.keys():
        list_of_energy_reduction.append(-energy_reduction_by_measure_cat[measure_cateogry])

    fig = go.Figure(go.Waterfall(
        measure= ['absolute'] + ['relative']*(len(list_of_measure_categories)-1),
        x=['Your Facility'] + list_of_measure_categories,
        y=[Total_final_energy] + list_of_energy_reduction
        ))
    fig.update_layout(
        title= 'Final Energy Reduction',
        xaxis_title='Measures',
        yaxis_title='Final Energy (MJ)'
        )

    fig.write_image(data_dir / "Graphs/energy waterfall.png")

    # Emissions
    list_of_measure_categories = list(emission_reduction_by_measure_cat.keys())
    list_of_emission_reduction = []

    for measure_cateogry in emission_reduction_by_measure_cat.keys():
        list_of_emission_reduction.append(-emission_reduction_by_measure_cat[measure_cateogry])

    fig = go.Figure(go.Waterfall(
        measure= ['absolute'] + ['relative']*(len(list_of_measure_categories)-1),
        x=['Your Facility'] + list_of_measure_categories,
        y=[Total_carbon_all] + list_of_emission_reduction
        ))
    fig.update_layout(
        title= 'Emission Reduction',
        xaxis_title='Measures',
        yaxis_title='Emissions (tCO2)'
        )

    fig.show()
    fig.write_image(data_dir / "Graphs/emissions waterfall.png")

    # Benchmarking Results Primary and Final Energy
    Total_primary_energy_after_measures = Total_primary_energy - sum(primary_energy_reduction_by_measure_cat.values())
    Total_final_energy_after_measures = Total_final_energy - sum(energy_reduction_by_measure_cat.values())

    # Plot graph
    fig, ax = plt.subplots(figsize=(7, 4))

    energy_use_comparison_labels = ['Your facility', 'Your target', 'Your facity \n with measures', 'National \n best practice', 'International \n best practice']
    energy_use_comparison_values = [Total_final_energy/10**6, Target_final/10**6, Total_final_energy_after_measures/10**6, 0, IBP_total_final_energy/10**6] # convert from MJ to TJ
    bar_colors = ['black', 'grey', 'royalblue', 'lime', 'green']

    ax.bar(energy_use_comparison_labels, energy_use_comparison_values, color=bar_colors)

    ax.set_ylabel('TJ/year')
    ax.set_title('Energy Use Comparisons (Final)')

    plt.savefig(data_dir / "Graphs/energy benchmark after measures.png")
    plt.close()
    # plt.show()

    # Benchmarking Results Carbon
    Total_carbon_direct_after_measures = Total_carbon_direct - sum(direct_carbon_reduction_by_measure_cat.values())
    Total_carbon_indirect_after_measures = Total_carbon_indirect - sum(indirect_carbon_reduction_by_measure_cat.values())
    Total_carbon_all_after_measures = Total_carbon_all - sum(emission_reduction_by_measure_cat.values())

    # Plot graphs
    fig, ax = plt.subplots(figsize=(9, 4))

    direct_carbon_comparison_labels = ['Your facility', 'Your target', 'Your facity \n with measures', 'National \n best practice', 'International \n best practice', 'International \n best practice \n with different fuel']
    direct_carbon_comparison_values = [Total_carbon_direct, Target_carbon_direct, Total_carbon_direct_after_measures, 0, IBP_carbon_direct, IBP_with_different_fuel_carbon_direct]
    bar_colors = ['black', 'grey', 'royalblue', 'lime', 'green', 'red']

    ax.bar(direct_carbon_comparison_labels, direct_carbon_comparison_values, color=bar_colors)

    ax.set_ylabel('tCO2/year')
    ax.set_title('Carbon Emissions Comparisons (Direct Energy)')

    plt.savefig(data_dir / "Graphs/direct energy co2 emissions benchmark after measures.png")
    plt.close()
    # plt.show()

    fig, ax = plt.subplots(figsize=(7, 4))

    indirect_carbon_comparison_labels = ['Your facility', 'Your target', 'Your facity \n with measures', 'National \n best practice', 'International \n best practice']
    indirect_carbon_comparison_values = [Total_carbon_indirect, Target_carbon_indirect, Total_carbon_indirect_after_measures, 0, IBP_carbon_indirect]
    bar_colors = ['black', 'grey', 'royalblue', 'lime', 'green']

    ax.bar(indirect_carbon_comparison_labels, indirect_carbon_comparison_values, color=bar_colors)

    ax.set_ylabel('tCO2/year')
    ax.set_title('Carbon Emissions Comparisons (indirect Energy)')

    plt.savefig(data_dir / "Graphs/indirect energy co2 emissions benchmark after measures.png")
    plt.close()
    # plt.show()

    fig, ax = plt.subplots(figsize=(7, 4))

    all_carbon_comparison_labels = ['Your facility', 'Your target', 'Your facity \n with measures', 'National \n best practice', 'International \n best practice']
    all_carbon_comparison_values = [Total_carbon_all, Target_carbon_all, Total_carbon_all_after_measures, 0, IBP_carbon_all]
    bar_colors = ['black', 'grey', 'royalblue', 'lime', 'green']

    ax.bar(all_carbon_comparison_labels, all_carbon_comparison_values, color=bar_colors)

    ax.set_ylabel('tCO2/year')
    ax.set_title('Carbon Emissions Comparisons (Energy and Process)')

    plt.savefig(data_dir / "Graphs/total co2 emissions benchmark after measures.png")
    plt.close()
    # plt.show()

    # Key values for reporting purposes
    Clinker_thermal_energy_intensity = Total_process_fuel / Total_clinker # MJ/tonne clinker
    Cement_electrical_energy_intensity = Total_process_electricity / Total_cement # kWh/tonne cement
    Cement_energy_intensity = Total_final_energy / Total_cement
    Cement_carbon_intensity = Total_carbon_all / Total_cement

    IBP_clinker_thermal_energy_intensity = IBP_total_fuel / Total_clinker
    IBP_cement_electrical_energy_intensity = IBP_total_electricity / Total_cement
    IBP_cement_energy_intensity = IBP_total_final_energy / Total_cement
    IBP_cement_carbon_intensity = IBP_carbon_all / Total_cement

    Cement_energy_intensity_after_measure = Total_final_energy_after_measures / Total_cement
    Cement_carbon_intensity_after_measure = Total_carbon_all_after_measures / Total_cement

    key_values_dict = {
        'Final energy (TJ)': {
            'Your facility before measures': round(Total_final_energy/10**6),
            'Your facility after measures': round(Total_final_energy_after_measures/10**6),
            'International Best Practice': round(IBP_total_final_energy/10**6)
            },
        'Cement energy intensity (MJ/tonne cement)': {
            'Your facility before measures': round(Cement_energy_intensity,2 ),
            'Your facility after measures': round(Cement_energy_intensity_after_measure, 2),
            'International Best Practice': round(IBP_cement_energy_intensity, 2)
            },
        'Total emissions (tCO2)': {
            'Your facility before measures': round(Total_carbon_all),
            'Your facility after measures': round(Total_carbon_all_after_measures),
            'International Best Practice': round(IBP_carbon_all)
            },
        'Cement emission intensity (tCO2/tonne cement)': {
            'Your facility before measures': round(Cement_carbon_intensity, 2),
            'Your facility after measures': round(Cement_carbon_intensity_after_measure, 2),
            'International Best Practice': round(IBP_cement_carbon_intensity, 2)
            }
        }

    key_values_df = pd.DataFrame.from_dict(key_values_dict, orient = 'index')

    with pd.ExcelWriter(json_folder / "key_values_in_excel.xlsx") as writer:
            key_values_df.to_excel(writer, sheet_name='values')        
            key_values_df = key_values_df.reset_index()

    # Retore initial energy and CO2 impacts before dumping back
    for measure_cateogry in all_DT_measures_dict.keys():
        for measure in all_DT_measures_dict[measure_cateogry].keys():
            
            all_DT_measures_dict[measure_cateogry][measure]["Energy Impacts (thermal)"] = all_DT_measures_dict[measure_cateogry][measure]["Energy Impacts (thermal) - initial"]
            all_DT_measures_dict[measure_cateogry][measure]["Energy Impacts (electricity)"] = all_DT_measures_dict[measure_cateogry][measure]["Energy Impacts (electricity) - initial"]
            all_DT_measures_dict[measure_cateogry][measure]["CO2 impacts (direct process)"] = all_DT_measures_dict[measure_cateogry][measure]["CO2 impacts (direct process) - initial"]

    with open(json_folder / 'all_DT_measures.json', 'w') as f:
        json.dump(all_DT_measures_dict, f, indent=4)
    all_dt_measures_dict = {}

    print("page 10 completed")

    return all_dt_measures_dict