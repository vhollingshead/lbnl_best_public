from PyQt6.QtWidgets import QLineEdit, QComboBox, QMessageBox

def validate_inputs(self):
    combo_errors = []
    input_errors = []

    invalid_combo_texts = {
        "Select fuel unit here",
        "Select electricity unit here",
        ""
    }
    for combo in self.findChildren(QComboBox):
        if combo.currentText().strip() in invalid_combo_texts:
            combo_errors.append(f"- Select a valid unit for: {combo.objectName()}")

    for field in self.findChildren(QLineEdit):
        if "input" in field.objectName().lower():
            if not field.text().strip():
                input_errors.append(f"- Enter a value for: {field.objectName()}")

    if combo_errors or input_errors:
        QMessageBox.critical(
            self,
            "Input Error",
            "Please ensure all required fields are filled out."
        )
        return False

    return True