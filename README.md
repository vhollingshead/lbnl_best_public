

#  Benchmarking and Energy Savings Tool (BEST)

LBNL's Energy Technologies Area is currently supporting Indonesia's energy goals through the adoption of benchmarking tools to develop baseline and target-setting frameworks. As part of this ongoing collaboration, LBNL is working to enhance the Benchmarking and Energy Savings Tool (BEST) Cement, which has been successfully implemented internationally and is being tailored for Indonesia's heavy industry subsectors. The tool enables companies to assess their energy and emissions performance against industry best practices and identify opportunities for improvement.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Features](#features)
- [Installation & Usage](#installation)
- [Terms & Conditions](#terms--conditions)
- [FAQ](#faq)
  - [How do I compile main.py into an executable on Mac and Windows? (This will include compiling the icon)](#how-do-i-compile-mainpy-into-an-executable-on-mac-and-windows)
  - [Why do Mac and Windows versions have a separate set of folders?](#why-do-mac-and-windows-versions-have-a-separate-set-of-folders)

---

## Project Structure

```text
00_BEST/
├── images/ # Stores icons, logos, and other image assets used in the application
│   ├── best_app_icon.icns
│   ├── best_app_icon.ico
│   ├── LandingPage_Abstract.png
│   ├── SidePage_Abstract.png
├── pages/ # Contains Python files for different pages in the application
│   ├── Page0_LandingPage.py
│   ├── Page1_AssessmentChoice.py
│   └── Page2_CostandEmission.py
│   └── ...
├── ui_files_latest/ # Holds XML files for UI design
│   ├── Page0_LandingPage_qwidget.ui
│   ├── Page1_AssessmentChoice_qwidget.ui
│   └── Page2_CostandEmission_qwidget.ui
│   └── ...
├── utils/ # Helper functions and utility scripts shared across the app
│   ├── calculations.py
│   ├── defaults.py
│   └── pdf_output.py
│   └── save_progress.py
│   └── warning_messages.py
├── main.py # The main entry point of the application
├── requirements.txt # Libraries and packages required to run main.py
├── resources_rc.py
└── resources.qrc
```

---

## Features
- Quick vs. Detailed assessment options for different user needs
- Support for scientific notation input (e.g., 1e10) for large-scale data entry
- Default value selection functionality with user override options
- Input field restrictions based on data type requirements
- PDF report generation capabilities
- Automated interpretation of results in final reports
- Save progress functionality for session continuity
- Report saving capabilities at completion 

---

## Installation & Usage

### Setup
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo

python -m venv pyqt6-env
source pyqt6-env/bin/activate
pip install -r requirements.txt
```

### Usage
```bash
python main.py
```

## Terms & Conditions

## FAQ

### How do I compile main.py into an executable on Mac and Windows?

### I want to change the backend calculations. How do I change the UI?

### Why do Mac and Windows versions have a separate set of folders?


