import json
import os
from PyQt6.QtWidgets import QLineEdit, QMessageBox, QComboBox
from PyQt6 import QtWidgets
from pathlib import Path
import sys

def get_user_data_dir(app_name="BEST Cement Tool"):
    # Mac users
    if sys.platform == "darwin":
        return Path.home() / app_name
    
    # Windows users
    elif sys.platform.startswith("win"):
        docs = Path.home() / "Documents"
        return docs / app_name
    
    else:  # Linux and others
        return Path.home() / ".config" / app_name


def load_progress_json(filename="Saved_BEST_Report_Progress.json"):
    data_dir = get_user_data_dir()
    filepath = data_dir / filename

    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        return None