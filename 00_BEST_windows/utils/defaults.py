import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout,
    QPushButton, QMainWindow, QLineEdit
)
from PyQt6 import QtWidgets

default_values_by_page = {
    "Page2": {
    "coal_input": "100",
    "coke_input": "180",
    "natural_gas_input": "6",
    "biomass_input": "40",
    "municipal_wastes_input": "40.0",

    "electricity_input": "0.2",
    "coal_hhv_input": "30",
    "coke_hhv_input": "26",
    "natural_gas_hhv_input": "52",
    "biomass_hhv_input": "20",
    "municipal_wastes_hvv_input": "22",
    "process_emission_per_metric_input": "0.507",
    "carbon_price_input": "20.0",
    "grid_co2_input": "0.5",

    "comboBox_electricity_unit": "$/kWh",
    "comboBox_coal_unit": "$/metric ton",
    "comboBox_coke_unit": "$/metric ton",
    "comboBox_natural_gas_unit": "$/MMBtu",
    "comboBox_biomass_unit": "$/metric ton",
    "comboBox_municipal_wastes_unit": "$/metric ton"
    },

    "Page3": {
    "limestone_input": "5200.0",
    "gypsum_input": "5000.0",
    "calcined_clay_input": "15000.0",
    "blast_furnace_slag_input": "25000.0",
    "other_slag_input": "35000.0",
    "fly_ash_input": "55000.0",
    "natural_pozzolans_input": "75.0",
    "type_1_input": "kiln_1",
    "type_2_input": "kiln_2",
    "production_1_input": "1000000",
    "production_2_input": "1000000",
    "pure_portland_cement_production_input": "1000000",
    "common_portland_cement_production_input": "1000000",
    "slag_cement_production_input": "1000000",
    "fly_ash_cement_production_input": "1000000",
    "pozzolana_cement_production_input": "1000000",
    "blended_cement_production_input": "1000000"}
}

def prefill_defaults(self):
    class_name = self.__class__.__name__  # e.g., 'Page1'
    defaults = default_values_by_page.get(class_name, {})

    for name, default in defaults.items():
        line_edit = self.findChild(QtWidgets.QLineEdit, name)
        if line_edit and not line_edit.text().strip():
            line_edit.setText(default)

        combo_box = self.findChild(QtWidgets.QComboBox, name)
        if combo_box and combo_box.currentText().strip() in ("", "Select fuel unit here", "Select electricity unit here"):
            combo_box.setCurrentText(default)


