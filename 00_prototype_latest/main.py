import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout,
    QPushButton, QMainWindow
)
from PyQt6.QtGui import QRegularExpressionValidator, QDesktopServices, QIcon
from PyQt6.QtCore import QRegularExpression, Qt, QSettings, QUrl
from PyQt6.QtWidgets import QMessageBox, QLabel, QDialog, QVBoxLayout, QPushButton, QTextBrowser
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox

print("importing pages")
from pages.Page0_LandingPage import Ui_LandingPage as LandingPageUI
print("importing assessment choice")
from pages.Page1_AssessmentChoice import Ui_Page1_AssessmentType as AssessmentChoiceUI
print("importing cost and emissions")
from pages.Page2_CostandEmission import Ui_Page2_CostandEmission as CostAndEmissionsUI  
print("importing production input")
from pages.Page3_ProductionInput import Ui_Page3_ProductionInput as ProductionInputUI
print("importing carbon capture")
from pages.Page4_CarbonCapture import Ui_Page4_CarbonCapture as CarbonCaptureUI
print("importing electricity generation input")
from pages.Page5_ElectricityGenerationInput import Ui_Page5_ElectricityGenerationInput as ElectricityGenerationInputUI

print("importing energy input")
from pages.Page6_EnergyInput import Ui_Page6_EnergyInput as EnergyInputUI
print("importing electricity input quick")
from pages.Page6_EnergyInputQuick import Ui_Page6_EnergyInputQuick as EnergyInputQuickUI
print("importing energy input detailed")
from pages.Page6_EnergyInputDetailed import Ui_Page6_EnergyInputDetailed as EnergyInputDetailedUI
print("importing energy input detailed 2")
from pages.Page6_EnergyInputDetailed_2 import Ui_Page6_EnergyInputDetailed_2 as EnergyInputDetailedUI_2

print("importing energy billing input")
from pages.Page7_EnergyBillingInput_Target import Ui_Page7_EnergyBillingInput as EnergyBillingInputUI

print("importing all measures - part 1")
from pages.Page8_1_AllMeasures import Ui_Page8_AllMeasures_1 as AllMeasuresUI_1
print("importing all measures - part 2a")
from pages.Page8_2a_AllMeasures import Ui_Page8_AllMeasures_2a as AllMeasuresUI_2a
print("importing all measures - part 2b")
from pages.Page8_2b_AllMeasures import Ui_Page8_AllMeasures_2b as AllMeasuresUI_2b
print("importing all measures - part 3")
from pages.Page8_3_AllMeasures import Ui_Page8_AllMeasures_3 as AllMeasuresUI_3

print("importing share page")
from pages.Page9_Share import Ui_Page9_Share as ShareUI

print("importing all measures")
from pages.Page10_AllDTMeasures import Ui_Page10_AllDTMeasures as AllDTMeasuresUI

print("importing sys")
import sys
import json
from utils.calculations import (Page2_Costs_and_Emissions_Input_Default_Update_Fields, 
                                Page3_Production_Input_Default_Update_Fields, 
                                Page4_Carbon_Capture_Input_Default_Update_Fields,
                                Page5_ElectricityGeneration_Input_Default_Update_Fields, 
                                Page6_Energy_Input_Default_Update_Fields,
                                Page6_Energy_Input_Quick_Default_Update_Fields,
                                Page6_Energy_Input_Detailed_Default_Update_Fields,
                                Page6_Energy_Input_Detailed_Default_Update_Fields_2,
                                Page7_Target_Default_Update_Fields,
                                Page8_All_Measures_1_Default_Update_Fields,
                                Page8_All_Measures_2a_Default_Update_Fields,
                                Page8_All_Measures_2b_Default_Update_Fields,
                                Page8_All_Measures_3_Default_Update_Fields,
                                EE_measure,
                                evaluate_EE_only_popup,
                                Page9_Share_Default_Update_Fields,
                                Page10_AllDTMeasures_Default_Update_Fields, 
                                Part_1_Detailed_Output)
                                
from utils.pdf_output import generate_part1_report, final_report_pdf

from utils.save_progress import load_progress_json
from utils.warning_messages import validate_inputs

from resources_rc import *
icon_ico = ":images/BEST_App_Logo.ico"
icon_icns = ":images/BEST_App_Logo.icns"
class LandingPage(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = LandingPageUI()
        self.ui.setupUi(self)
        self.ui.get_started.clicked.connect(self.next_page)
        self.ui.resumeBtn.clicked.connect(self.resume_progress)

    def next_page(self):
        self.stack.setCurrentIndex(1)
        self.parent.setFixedSize(1260, 700)

    def resume_progress(self):
        self.parent.resume_previous_session()
        self.parent.setFixedSize(1260, 700)
        self.stack.setCurrentIndex(1)


class Page1(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.ui = AssessmentChoiceUI()
        self.ui.setupUi(self)
        self.parent = parent

        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

    def next_page(self):
        assessment_choice = self.ui.comboBox_assessment_type.currentText().strip()
        self.parent.assessment_choice = self.ui.comboBox_assessment_type.currentText().strip()

        if assessment_choice == "Select Assessment Type":
            QMessageBox.information(self, "Incomplete Selection", "Please choose 'Detailed Assessment' or 'Quick Assessment' before proceeding.")
            return
        
        self.stack.setCurrentWidget(self.parent.page2)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()
        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()
        return data
    
    def save_current_and_all(self):
        if self.ui.comboBox_assessment_type.currentText().strip() == "Select Assessment Type:":
            QMessageBox.warning(self, "Save Error", "Please choose 'Detailed Assessment' or 'Quick Assessment' before saving progress.")
            return
        if self.parent:
            self.parent.save_all_pages()

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)


class Page2(QWidget):
    from utils.defaults import prefill_defaults

    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = CostAndEmissionsUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.defaultBtn.clicked.connect(self.prefill_defaults)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        sci_validator = QRegularExpressionValidator(QRegularExpression(r'^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$'))

        self.ui.coal_input.setValidator(sci_validator)
        self.ui.coke_input.setValidator(sci_validator)
        self.ui.natural_gas_input.setValidator(sci_validator)
        self.ui.biomass_input.setValidator(sci_validator)
        self.ui.municipal_wastes_input.setValidator(sci_validator)
        self.ui.electricity_input.setValidator(sci_validator)
        self.ui.coal_hhv_input.setValidator(sci_validator)
        self.ui.coke_hhv_input.setValidator(sci_validator)
        self.ui.natural_gas_hhv_input.setValidator(sci_validator)
        self.ui.biomass_hhv_input.setValidator(sci_validator)
        self.ui.municipal_wastes_hvv_input.setValidator(sci_validator)
        self.ui.process_emission_per_metric_input.setValidator(sci_validator)
        self.ui.carbon_price_input.setValidator(sci_validator)
        self.ui.grid_co2_input.setValidator(sci_validator)

    def warning_check(self):
        if not validate_inputs(self):
            return  
        else:
            self.stack.setCurrentWidget(self.parent.page3)

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page1)

    def next_page(self):
        Page2_Costs_and_Emissions_Input_Default_Update_Fields(self)
        self.warning_check()

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()
        return data
    
    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  
            
    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page3(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = ProductionInputUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)
        

        sci_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
        )
        
        self.ui.limestone_input.setValidator(sci_validator)
        self.ui.gypsum_input.setValidator(sci_validator)
        self.ui.calcined_clay_input.setValidator(sci_validator)
        self.ui.blast_furnace_slag_input.setValidator(sci_validator)
        self.ui.other_slag_input.setValidator(sci_validator)
        self.ui.fly_ash_input.setValidator(sci_validator)
        self.ui.natural_pozzolans_input.setValidator(sci_validator)
        
        self.ui.production_1_input.setValidator(sci_validator)
        self.ui.production_2_input.setValidator(sci_validator)

        self.ui.pure_portland_cement_production_input.setValidator(sci_validator)
        self.ui.common_portland_cement_production_input.setValidator(sci_validator)
        self.ui.slag_cement_production_input.setValidator(sci_validator)
        self.ui.fly_ash_cement_production_input.setValidator(sci_validator)
        self.ui.pozzolana_cement_production_input.setValidator(sci_validator)
        self.ui.blended_cement_production_input.setValidator(sci_validator)
        

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page2)

    def next_page(self):
        Page3_Production_Input_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page4)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page4(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = CarbonCaptureUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)
        

        sci_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
        )

        self.ui.co2_captured_input.setPlaceholderText("0")
        self.ui.co2_captured_input.setValidator(sci_validator)
        
    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page3)

    def next_page(self):
        Page4_Carbon_Capture_Input_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page5)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page5(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = ElectricityGenerationInputUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)
        

        sci_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
        )
        
        self.ui.total_energy_purchased_input.setValidator(sci_validator)
        self.ui.total_electricity_generated_onsite_input.setValidator(sci_validator)
        self.ui.electricity_generated_input.setValidator(sci_validator)
        self.ui.waste_heat_input_page5.setValidator(sci_validator)
        self.ui.coal_input_page5.setValidator(sci_validator)
        self.ui.coke_input_page5.setValidator(sci_validator)
        self.ui.natural_gas_input_page5.setValidator(sci_validator)
        self.ui.biomass_input_page5.setValidator(sci_validator)
        self.ui.municipal_wastes_input_page5.setValidator(sci_validator)
        self.ui.onsite_renewables_input_page5.setValidator(sci_validator)
        

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page4)

    def next_page(self):
        Page5_ElectricityGeneration_Input_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page6)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()
        
        # Collect from QCheckBox
        for cb in self.findChildren(QCheckBox):
            key = cb.objectName()
            data[key] = cb.isChecked()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

        for cb in self.findChildren(QCheckBox):
            key = cb.objectName()
            if key in data_dict:
                cb.setChecked(data_dict[key])

class Page6(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = EnergyInputUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)

        self.ui.ball_mill_raw_input.setValidator(percent_validator())
        self.ui.ball_mill_cement_input.setValidator(percent_validator())
        self.ui.vert_roller_mill_raw_input.setValidator(percent_validator())
        self.ui.vert_roller_mill_fuel_input.setValidator(percent_validator())
        self.ui.vert_roller_mill_cement_input.setValidator(percent_validator())
        self.ui.horizontal_roller_mill_raw_input.setValidator(percent_validator())
        self.ui.horizontal_roller_mill_fuel_input.setValidator(percent_validator())
        self.ui.horizontal_roller_mill_cement_input.setValidator(percent_validator())

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page5)

    def next_page(self):
        Page6_Energy_Input_Default_Update_Fields(self)
        if self.parent.assessment_choice == "Quick Assessment":
            self.stack.setCurrentWidget(self.parent.page6_Quick) # Page6_Quick
        else:
            self.stack.setCurrentWidget(self.parent.page6_Detailed) # Page6_Detailed

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page6_Quick(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = EnergyInputQuickUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        sci_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
        )

        self.ui.coal_quick_input_page6.setValidator(sci_validator)
        self.ui.coke_quick_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_quick_input_page6.setValidator(sci_validator)
        self.ui.biomass_quick_input_page6.setValidator(sci_validator)
        self.ui.msw_quick_input_page6.setValidator(sci_validator)
        self.ui.electricity_quick_input_page6.setValidator(sci_validator)
        self.ui.electricity_input_page6.setValidator(sci_validator)

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page6)

    def next_page(self):
        Page6_Energy_Input_Quick_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page7)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page6_Detailed(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = EnergyInputDetailedUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        sci_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
        )

        self.ui.coal_conveying_input_page6.setValidator(sci_validator)
        self.ui.coal_preblending_input_page6.setValidator(sci_validator)
        self.ui.coal_crushing_input_page6.setValidator(sci_validator)
        self.ui.coal_grinding_input_page6_2.setValidator(sci_validator)
        self.ui.coal_additive_prep_input_page6.setValidator(sci_validator)
        self.ui.coal_additive_dry_input_page6.setValidator(sci_validator)
        self.ui.coal_fuelprep_input_page6.setValidator(sci_validator)
        self.ui.coal_homo_input_page6.setValidator(sci_validator)
        self.ui.coal_kiln_input_page6.setValidator(sci_validator)
        self.ui.coal_kiln_precalciner_input_page6.setValidator(sci_validator)

        self.ui.coke_conveying_input_page6.setValidator(sci_validator)
        self.ui.coke_preblending_input_page6.setValidator(sci_validator)
        self.ui.coke_crushing_input_page6.setValidator(sci_validator)
        self.ui.coke_grinding_input_page6_2.setValidator(sci_validator)
        self.ui.coke_additive_prep_input_page6.setValidator(sci_validator)
        self.ui.coke_additive_dry_input_page6.setValidator(sci_validator)
        self.ui.coke_fuelprep_input_page6.setValidator(sci_validator)
        self.ui.coke_homo_input_page6.setValidator(sci_validator)
        self.ui.coke_kiln_input_page6.setValidator(sci_validator)
        self.ui.coke_kiln_precalciner_input_page6.setValidator(sci_validator)
        
        self.ui.natural_gas_conveying_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_preblending_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_crushing_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_grinding_input_page6_2.setValidator(sci_validator)
        self.ui.natural_gas_additive_prep_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_additive_dry_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_fuelprep_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_homo_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_kiln_input_page6.setValidator(sci_validator)
        self.ui.natural_gas_kiln_precalciner_input_page6.setValidator(sci_validator)
        
        self.ui.biomass_conveying_input_page6.setValidator(sci_validator)
        self.ui.biomass_preblending_input_page6.setValidator(sci_validator)
        self.ui.biomass_crushing_input_page6.setValidator(sci_validator)
        self.ui.biomass_grinding_input_page6_2.setValidator(sci_validator)
        self.ui.biomass_additive_prep_input_page6.setValidator(sci_validator)
        self.ui.biomass_additive_dry_input_page6.setValidator(sci_validator)
        self.ui.biomass_fuelprep_input_page6.setValidator(sci_validator)
        self.ui.biomass_homo_input_page6.setValidator(sci_validator)
        self.ui.biomass_kiln_input_page6.setValidator(sci_validator)
        self.ui.biomass_kiln_precalciner_input_page6.setValidator(sci_validator)

        self.ui.msw_conveying_input_page6.setValidator(sci_validator)
        self.ui.msw_preblending_input_page6.setValidator(sci_validator)
        self.ui.msw_crushing_input_page6.setValidator(sci_validator)
        self.ui.msw_grinding_input_page6_2.setValidator(sci_validator)
        self.ui.msw_additive_prep_input_page6.setValidator(sci_validator)
        self.ui.msw_additive_dry_input_page6.setValidator(sci_validator)
        self.ui.msw_fuelprep_input_page6.setValidator(sci_validator)
        self.ui.msw_homo_input_page6.setValidator(sci_validator)
        self.ui.msw_kiln_input_page6.setValidator(sci_validator)
        self.ui.msw_kiln_precalciner_input_page6.setValidator(sci_validator)

        self.ui.electricity_conveying_input_page6.setValidator(sci_validator)
        self.ui.electricity_preblending_input_page6.setValidator(sci_validator)
        self.ui.electricity_crushing_input_page6.setValidator(sci_validator)
        self.ui.electricity_grinding_input_page6_2.setValidator(sci_validator)
        self.ui.electricity_additive_prep_input_page6.setValidator(sci_validator)
        self.ui.electricity_additive_dry_input_page6.setValidator(sci_validator)
        self.ui.electricity_fuelprep_input_page6.setValidator(sci_validator)
        self.ui.electricity_homo_input_page6.setValidator(sci_validator)
        self.ui.electricity_kiln_input_page6.setValidator(sci_validator)
        self.ui.electricity_kiln_precalciner_input_page6.setValidator(sci_validator)

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page6)

    def next_page(self):
        Page6_Energy_Input_Detailed_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page6_Detailed_2)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page6_Detailed_2(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = EnergyInputDetailedUI_2()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        sci_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
        )

        self.ui.coal_kiln_kiln_page6_b.setValidator(sci_validator)
        self.ui.coal_kiln_cooler_page6_b.setValidator(sci_validator)
        self.ui.coal_cement_grinding_page6_b.setValidator(sci_validator)
        self.ui.coal_other_conveying_page6_b.setValidator(sci_validator)
        self.ui.coal_non_production_page6_b.setValidator(sci_validator)
        self.ui.coal_air_pollution_page6_b.setValidator(sci_validator)
        self.ui.coal_ccus_page6_b.setValidator(sci_validator)

        self.ui.coke_kiln_kiln_page6_b.setValidator(sci_validator)
        self.ui.coke_kiln_cooler_page6_b.setValidator(sci_validator)
        self.ui.coke_cement_grinding_page6_b.setValidator(sci_validator)
        self.ui.coke_other_conveying_page6_b.setValidator(sci_validator)
        self.ui.coke_non_production_page6_b.setValidator(sci_validator)
        self.ui.coke_air_pollution_page6_b.setValidator(sci_validator)
        self.ui.coke_ccus_page6_b.setValidator(sci_validator)

        self.ui.natural_gas_kiln_kiln_page6_b.setValidator(sci_validator)
        self.ui.natural_gas_kiln_cooler_page6_b.setValidator(sci_validator)
        self.ui.natural_gas_cement_grinding_page6_b.setValidator(sci_validator)
        self.ui.natural_gas_other_conveying_page6_b.setValidator(sci_validator)
        self.ui.natural_gas_non_production_page6_b.setValidator(sci_validator)
        self.ui.natural_gas_air_pollution_page6_b.setValidator(sci_validator)
        self.ui.natural_gas_ccus_page6_b.setValidator(sci_validator)

        self.ui.biomass_kiln_kiln_page6_b.setValidator(sci_validator)
        self.ui.biomass_kiln_cooler_page6_b.setValidator(sci_validator)
        self.ui.biomass_cement_grinding_page6_b.setValidator(sci_validator)
        self.ui.biomass_other_conveying_page6_b.setValidator(sci_validator)
        self.ui.biomass_non_production_page6_b.setValidator(sci_validator)
        self.ui.biomass_air_pollution_page6_b.setValidator(sci_validator)
        self.ui.biomass_ccus_page6_b.setValidator(sci_validator)

        self.ui.msw_kiln_kiln_page6_b.setValidator(sci_validator)
        self.ui.msw_kiln_cooler_page6_b.setValidator(sci_validator)
        self.ui.msw_cement_grinding_page6_b.setValidator(sci_validator)
        self.ui.msw_other_conveying_page6_b.setValidator(sci_validator)
        self.ui.msw_non_production_page6_b.setValidator(sci_validator)
        self.ui.msw_air_pollution_page6_b.setValidator(sci_validator)
        self.ui.msw_ccus_page6_b.setValidator(sci_validator)

        self.ui.electricity_kiln_kiln_page6_b.setValidator(sci_validator)
        self.ui.electricity_kiln_cooler_page6_b.setValidator(sci_validator)
        self.ui.electricity_cement_grinding_page6_b.setValidator(sci_validator)
        self.ui.electricity_other_conveying_page6_b.setValidator(sci_validator)
        self.ui.electricity_non_production_page6_b.setValidator(sci_validator)
        self.ui.electricity_air_pollution_page6_b.setValidator(sci_validator)
        self.ui.electricity_ccus_page6_b.setValidator(sci_validator)

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page6_Detailed)

    def next_page(self):
        Page6_Energy_Input_Detailed_Default_Update_Fields_2(self)
        self.stack.setCurrentWidget(self.parent.page7)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page7(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = EnergyBillingInputUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)

        self.ui.energy_percent_reduction_input.setValidator(percent_validator())
        self.ui.direct_percent_reduction_input.setValidator(percent_validator())
        self.ui.indirect_percent_reduction_input.setValidator(percent_validator())
        self.ui.overall_percent_reduction_input.setValidator(percent_validator())

    def go_to_previous(self):

        if self.parent.assessment_choice == "Quick Assessment":
            self.stack.setCurrentWidget(self.parent.page6_Quick) # Page6_Quick
        else:
            self.stack.setCurrentWidget(self.parent.page6_Detailed_2) # Page6_Detailed_2

    def next_page(self):
        Page7_Target_Default_Update_Fields(self)
        Part_1_Detailed_Output(self)
        generate_part1_report(self) 
        self.stack.setCurrentWidget(self.parent.page8_1)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page8_1(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = AllMeasuresUI_1()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)
        

        sci_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
        )

        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)
        
        
        
        self.ui.page8_1_potential_input.setValidator(percent_validator())
        self.ui.page8_1_potential_input_2.setValidator(percent_validator())
        self.ui.page8_1_potential_input_3.setValidator(percent_validator())
        self.ui.page8_1_potential_input_4.setValidator(percent_validator())
        self.ui.page8_1_potential_input_5.setValidator(percent_validator())
        self.ui.page8_1_potential_input_6.setValidator(percent_validator())
        self.ui.page8_1_potential_input_7.setValidator(percent_validator())
        self.ui.page8_1_potential_input_8.setValidator(percent_validator())
        self.ui.page8_1_potential_input_9.setValidator(percent_validator())
        self.ui.page8_1_potential_input_10.setValidator(percent_validator())
        self.ui.page8_1_potential_input_11.setValidator(percent_validator())
        self.ui.page8_1_potential_input_12.setValidator(percent_validator())

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page7)

    def next_page(self):
        Page8_All_Measures_1_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page8_2a)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page8_2a(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = AllMeasuresUI_2a()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)
        
        self.ui.page_8_2a_input.setValidator(percent_validator())
        self.ui.page_8_2a_input_2.setValidator(percent_validator())
        self.ui.page_8_2a_input_3.setValidator(percent_validator())
        self.ui.page_8_2a_input_4.setValidator(percent_validator())
        self.ui.page_8_2a_input_5.setValidator(percent_validator())
        self.ui.page_8_2a_input_6.setValidator(percent_validator())
        self.ui.page_8_2a_input_7.setValidator(percent_validator())
        self.ui.page_8_2a_input_8.setValidator(percent_validator())
        self.ui.page_8_2a_input_9.setValidator(percent_validator())
        

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page8_1)

    def next_page(self):
        Page8_All_Measures_2a_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page8_2b)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page8_2b(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = AllMeasuresUI_2b()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)

        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)
        
        self.ui.page_8_2b_input.setValidator(percent_validator())
        self.ui.page_8_2b_input_2.setValidator(percent_validator())
        self.ui.page_8_2b_input_3.setValidator(percent_validator())
        self.ui.page_8_2b_input_4.setValidator(percent_validator())
        self.ui.page_8_2b_input_5.setValidator(percent_validator())
        self.ui.page_8_2b_input_6.setValidator(percent_validator())
        self.ui.page_8_2b_input_7.setValidator(percent_validator())
        self.ui.page_8_2b_input_8.setValidator(percent_validator())
        self.ui.page_8_2b_input_9.setValidator(percent_validator())

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page8_2a)

    def next_page(self):
        Page8_All_Measures_2b_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page8_3)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page8_3(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = AllMeasuresUI_3()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)
        
        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)
        
        self.ui.page_8_3_input.setValidator(percent_validator())
        self.ui.page_8_3_input_2.setValidator(percent_validator())
        self.ui.page_8_3_input_3.setValidator(percent_validator())
        self.ui.page_8_3_input_4.setValidator(percent_validator())
        self.ui.page_8_3_input_5.setValidator(percent_validator())
        self.ui.page_8_3_input_6.setValidator(percent_validator())
        self.ui.page_8_3_input_7.setValidator(percent_validator())
        self.ui.page_8_3_input_8.setValidator(percent_validator())
        self.ui.page_8_3_input_9.setValidator(percent_validator())
        self.ui.page_8_3_input_10.setValidator(percent_validator())
        self.ui.page_8_3_input_11.setValidator(percent_validator())
        self.ui.page_8_3_input_12.setValidator(percent_validator())
        self.ui.page_8_3_input_13.setValidator(percent_validator())
        self.ui.page_8_3_input_14.setValidator(percent_validator()) 

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page8_2b)

    def next_page(self):
        Page8_All_Measures_3_Default_Update_Fields(self)
        evaluate_EE_only_popup(self)
        EE_measure(self)
        self.stack.setCurrentWidget(self.parent.page9)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page9(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = ShareUI()
        self.ui.setupUi(self)
        self.ui.nextBtn.clicked.connect(self.next_page)
        self.ui.backBtn.clicked.connect(self.go_to_previous)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)
        

        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)
        
        self.ui.coal_input_page9.setValidator(percent_validator())
        self.ui.coke_input_page9.setValidator(percent_validator())
        self.ui.natural_gas_input_page9.setValidator(percent_validator())
        self.ui.biomass_input_page9.setValidator(percent_validator())
        self.ui.msw_input_page9.setValidator(percent_validator())
        self.ui.share_electricity_input_page9.setValidator(percent_validator())

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page8_3)

    def next_page(self):
        Page9_Share_Default_Update_Fields(self)
        self.stack.setCurrentWidget(self.parent.page10)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()

        return data

    def save_current_and_all(self):
        if self.parent:
            
            self.parent.save_all_pages()  

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

class Page10(QWidget):
    from utils.pdf_output import generate_report_reportlab  

    def __init__(self, stack, parent=None):
        super().__init__()
        self.stack = stack
        self.parent = parent
        self.ui = AllDTMeasuresUI()
        self.ui.setupUi(self)
        self.ui.pdfBtn.clicked.connect(self.generate_report)
        self.ui.saveBtn.clicked.connect(self.save_current_and_all)
        self.ui.backBtn.clicked.connect(self.go_to_previous)

        def percent_validator():
            regex = QRegularExpression(r"^(?:|100(?:\.0{0,2})?|\d{1,2}(?:\.\d{0,2})?)$")
            return QRegularExpressionValidator(regex)
        
        self.ui.page_10_input.setValidator(percent_validator())
        self.ui.page_10_input_2.setValidator(percent_validator())
        self.ui.page_10_input_3.setValidator(percent_validator())
        self.ui.page_10_input_4.setValidator(percent_validator())
        self.ui.page_10_input_5.setValidator(percent_validator())
        self.ui.page_10_input_6.setValidator(percent_validator())
        self.ui.page_10_input_7.setValidator(percent_validator())
        self.ui.page_10_input_8.setValidator(percent_validator())
        self.ui.page_10_input_9.setValidator(percent_validator())

    def go_to_previous(self):
        self.stack.setCurrentWidget(self.parent.page9)

    def generate_report(self):
        Page10_AllDTMeasures_Default_Update_Fields(self)
        self.save_current_and_all()
        final_report_pdf(self)

    def collect_page_data(self):
        data = {}
        for widget in self.findChildren(QLineEdit):
            data[widget.objectName()] = widget.text()

        # Collect from QComboBox
        for combo in self.findChildren(QComboBox):
            data[combo.objectName()] = combo.currentText()
        return data
    
    def save_current_and_all(self):
        if self.parent:
            self.parent.save_all_pages()

    def load_values_from_dict(self, data_dict):
        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name in data_dict:
                widget.setText(data_dict[name])

        for combo in self.findChildren(QComboBox):
            name = combo.objectName()
            if name in data_dict:
                index = combo.findText(data_dict[name])
                if index != -1:
                    combo.setCurrentIndex(index)

LICENSE_HTML_MAC = (
    '<b>Licensed Visual Content</b><br><br>'
    'This application uses design elements licensed under Canva’s Free Content License '
    'and Adobe Stock’s Standard License. End users are not permitted to extract, reuse, '
    'modify, redistribute, or make separate use of visual content embedded in the app. '
    'By using this application, you agree not to attempt to access or repurpose any '
    'licensed media included herein.<br><br>'
    'Full license terms: '
    '<a href="https://www.canva.com/policies/content-license-agreement/">Canva License</a> , '
    '<a href="https://www.adobe.com/content/dam/cc/en/legal/terms/enterprise/pdfs/PSLT-Stock-WW-2024v1.pdf">Adobe Stock License</a>'
    '<br><br>'
    '<b>For Mac Users:</b><br>'
    'To ensure the best experience, we recommend using the default Light Mode.'
)

LICENSE_HTML_WINDOWS = (
    '<b>Licensed Visual Content</b><br><br>'
    'This application uses design elements licensed under Canva’s Free Content License '
    'and Adobe Stock’s Standard License. End users are not permitted to extract, reuse, '
    'modify, redistribute, or make separate use of visual content embedded in the app. '
    'By using this application, you agree not to attempt to access or repurpose any '
    'licensed media included herein.<br><br>'
    'Full license terms: '
    '<a href="https://www.canva.com/policies/content-license-agreement/">Canva License</a> , '
    '<a href="https://www.adobe.com/content/dam/cc/en/legal/terms/enterprise/pdfs/PSLT-Stock-WW-2024v1.pdf">Adobe Stock License</a>'
    '<br><br>'
)

class LicenseDialog(QDialog):
    def __init__(self, message_html: str, parent=None, width=520, length=300):
        super().__init__(parent)
        self.setWindowTitle("Terms and Conditions")
        self.setWindowIcon(QIcon(icon_ico))
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)

        viewer = QTextBrowser(self)
        viewer.setOpenExternalLinks(False)  
        viewer.setOpenLinks(False)
        viewer.setHtml(message_html)
        viewer.setReadOnly(True)
        viewer.setFixedWidth(width)  
        viewer.anchorClicked.connect(self._open_link)  
        layout.addWidget(viewer)

        accept_btn = QPushButton("I Accept", self)
        accept_btn.setDefault(True)
        accept_btn.clicked.connect(self.accept)
        layout.addWidget(accept_btn)

        self.setLayout(layout)
        self.adjustSize()
        self.setFixedWidth(width + 40) 
        self.setFixedHeight(length)

    def reject(self):
        pass

    def _open_link(self, qurl: QUrl):
        QDesktopServices.openUrl(qurl)




class MainApp(QMainWindow):
    from utils.save_progress import get_user_data_dir, load_progress_json
    from pathlib import Path
    import sys
    import os

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(icon_ico))
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.landing_page = LandingPage(self.stack, self)
        self.page1 = Page1(self.stack, self)
        self.page2 = Page2(self.stack, self)
        self.page3 = Page3(self.stack, self)
        self.page4 = Page4(self.stack, self)
        self.page5 = Page5(self.stack, self)
        self.page6 = Page6(self.stack, self)
        self.page6_Quick = Page6_Quick(self.stack, self)
        self.page6_Detailed = Page6_Detailed(self.stack, self)
        self.page6_Detailed_2 = Page6_Detailed_2(self.stack, self)
        self.page7 = Page7(self.stack, self)
        self.page8_1 = Page8_1(self.stack, self)
        self.page8_2a = Page8_2a(self.stack, self)
        self.page8_2b = Page8_2b(self.stack, self)
        self.page8_3 = Page8_3(self.stack, self)
        self.page9 = Page9(self.stack, self)
        self.page10 = Page10(self.stack, self)

        self.stack.addWidget(self.landing_page)  
        self.stack.addWidget(self.page1)         
        self.stack.addWidget(self.page2)         
        self.stack.addWidget(self.page3)         
        self.stack.addWidget(self.page4)         
        self.stack.addWidget(self.page5)         
        self.stack.addWidget(self.page6)         
        self.stack.addWidget(self.page6_Quick)         
        self.stack.addWidget(self.page6_Detailed)         
        self.stack.addWidget(self.page6_Detailed_2)
        self.stack.addWidget(self.page7)         
        self.stack.addWidget(self.page8_1)         
        self.stack.addWidget(self.page8_2a)         
        self.stack.addWidget(self.page8_2b)         
        self.stack.addWidget(self.page8_3)         
        self.stack.addWidget(self.page9)         
        self.stack.addWidget(self.page10)         
        self.stack.setCurrentIndex(0)
        self.setWindowTitle("BEST Cement")
        self.setFixedSize(1260, 700)

    def get_user_data_dir(self, app_name="BEST Cement Tool"):
            from pathlib import Path
            # Mac users
            if sys.platform == "darwin":
                return self.Path.home() / app_name
            
            # Windows users
            elif sys.platform.startswith("win"):
                docs = Path.home() / "Documents"
                return docs / app_name
            
            else:  # Linux and others
                return self.Path.home() / ".config" / app_name
            

    def save_all_pages(self, filename="Saved_BEST_Report_Progress.json"):

        all_data = {}
        for page in [self.page1, self.page2, self.page3, self.page4, self.page5, self.page6, self.page6_Quick, self.page6_Detailed, self.page6_Detailed_2, self.page7, self.page8_1, self.page8_2a, self.page8_2b, self.page8_3, self.page9, self.page10]:
            if hasattr(page, "collect_page_data"):
                all_data.update(page.collect_page_data())

        data_dir = self.get_user_data_dir()

        json_folder = data_dir / "Saved Progress"
        json_folder.mkdir(parents=True, exist_ok=True)

        filepath = json_folder / filename

        with open(filepath, "w") as f:
            json.dump(all_data, f, indent = 2)

        QMessageBox.information(
        self,
        "Progress Saved", f"Your progress has been saved.")

    def resume_previous_session(self):
        from utils.save_progress import load_progress_json
        filename="Saved_BEST_Report_Progress.json"

        data_dir = self.get_user_data_dir()
        json_folder = data_dir / "Saved Progress"

        filepath = json_folder / filename

        if filepath.exists():

            data = load_progress_json(filepath)
            for page in [self.page1, self.page2, self.page3, self.page4, self.page5, self.page6, self.page6_Quick, self.page6_Detailed, self.page6_Detailed_2, self.page7, self.page8_1, self.page8_2a, self.page8_2b, self.page8_3, self.page9, self.page10]:
                if hasattr(page, "load_values_from_dict"):
                    page.load_values_from_dict(data)
            QMessageBox.information(self, "Session Resumed", "Your previous responses have been restored. Please review each page for accuracy.")
        else:
            QMessageBox.information(self, "Session Resumed", "You do not have a saved session at this time.")
        

# --- App Launcher ---
if __name__ == "__main__":

    app = QApplication(sys.argv)

    if sys.platform.startswith("darwin"):
        dlg = LicenseDialog(LICENSE_HTML_MAC)
        dlg.exec()
    else:
        dlg = LicenseDialog(LICENSE_HTML_WINDOWS)
        dlg.exec()

    # Base stylesheet (shared across platforms)
    base_stylesheet = """
    

    QPushButton {
        background-color: #00313c;  /* Dark Blue */
        color: white;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        border-radius: 6px;
        min-width: 70px;
        min-height: 15px;
    }

    QPushButton:hover {
        background-color: #45a049;
    }

    QPushButton:pressed {
        background-color: #3e8e41;
    }

    QPushButton#saveBtn {
        background-color: white;
        color: #00313c;
    }

    QPushButton#saveBtn:hover {
        background-color: #45a049;
        color: white;
    }

    QLineEdit {
        border-radius: 10px;
        padding: 5px;
        background-color: #ffffff; 
    }

    QMessageBox QPushButton {
        background-color: #00313c;
        color: white;
        border-radius: 5px;
        padding: 6px 12px;
        min-width: 60px;
    }

    QMessageBox QPushButton:hover {
        background-color: #45a049;
    }

    QMessageBox QPushButton:pressed {
        background-color: #3e8e41;
    }
    """

    if sys.platform.startswith("win"):  
        base_stylesheet += """
        /* Page background (example) */
        QWidget { 
            background: #eeefee; 
        }

        /* GroupBox */
        QGroupBox {
            background-color: #e8e8e8;      /* slightly darker than page */
            border: 1px solid #dfdfdf;
            border-radius: 8px;
            padding: 12px;                  /* inner padding for contents */
            padding-top: 20px;              /* room for the title text */
            margin-top: 16px;               /* external spacing */
        }

        /* Title styling */
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;  /* title sits at top-left of frame */
            padding: 0 6px;
            margin-top: -9px;
            background-color: #eeefee;      /* match page background so it sits "on top" */
            color: #000;
            font: bold 13px "Segoe UI", -apple-system, sans-serif;
            border-radius: 6px;
        }

        /* Any widget inside the group box to inherit background */
        QGroupBox > QWidget {
            background-color: transparent;
        }

        /* All QLabel inside any QGroupBox should be transparent too */
        QGroupBox QLabel {
            background-color: transparent;
        }

        QPushButton {
        background-color: #00313c;
        color: white;
        border: none;
            }

        QPushButton:hover { background-color: #45a049; }
        QPushButton:pressed { background-color: #3e8e41; }

        QGroupBox QComboBox {
        background-color: #ffffff; 
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 2px 6px;
        min-width: 125px;
    }

        /* Windows-specific tweak for line edits */
        QLineEdit {
            min-width: 125px;
            background-color: #ffffff; 
        }
        
        /* QComboBox */
        QComboBox {
            min-width: 125px;
            background-color: #ffffff; 
            border: 1px solid #cccccc;
        }

        /* QMessageBox */
        QMessageBox {
            background-color: #eeefee;
            border-radius: 8px;
        }

        QLabel#label,
        QLabel#label_2,
        QLabel#label_3,
        QLabel#label_4,
        QLabel#label_5,
        QLabel#label_6,
        QLabel#label_7,
        QLabel#label_8,
        QLabel#label_9,
        QLabel#label_10,
        QLabel#label_11,
        QLabel#label_12,
        QLabel#label_13,
        QLabel#label_14,
        QLabel#label_15,
        QLabel#label_16,
        QLabel#summary_label,
        QLabel#select_label {
            font-size: 9pt;
        }

        QLabel#page_8_3_header_2,
        QLabel#page_8_3_header_3 {
            font-size: 9pt;
        }

        """


    app.setStyleSheet(base_stylesheet)

    window = MainApp()
    window.show()
    sys.exit(app.exec())