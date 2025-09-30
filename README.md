
<img width="1366" height="768" alt="Copy of Copy of BEST_front_Center" src="https://github.com/user-attachments/assets/afa1b6e0-eaf0-43d8-b3de-7ae5b65f95e8" />


#  Benchmarking and Energy Savings Tool (BEST)

LBNL's Energy Technologies Area is currently supporting Indonesia's energy goals through the adoption of benchmarking tools to develop baseline and target-setting frameworks. As part of this ongoing collaboration, LBNL is working to enhance the Benchmarking and Energy Savings Tool (BEST) Cement, which has been successfully implemented internationally and is being tailored for Indonesia's heavy industry subsectors. The tool enables companies to assess their energy and emissions performance against industry best practices and identify opportunities for improvement.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Features](#features)
- [Installation & Usage](#installation)
- [Terms & Conditions](#terms--conditions)
- [Application Maintenance](#application-maintenance)
  - [How do I compile main.py into an executable on Mac and Windows? (This will include compiling the icon)](#how-do-i-compile-mainpy-into-an-executable-on-mac-and-windows)
  - [How do I make changes to the UI?](#how-do-i-make-changes-to-the-ui)
  - [Why do Mac and Windows versions have a separate set of folders?](#why-do-mac-and-windows-versions-have-a-separate-set-of-folders)

---

## Project Structure

```text
00_BEST/
├── images/ # Stores icons, logos, and other image assets used in the application
│   ├── BEST_App_Icon.icns
│   ├── BEST_App_Icon.ico
│   ├── BEST_landing_abstract.png
│   ├── BEST_side_abstract.png
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
git clone https://github.com/vhollingshead/lbnl_best_public.git
cd 00_BEST

# Mac virtual environment setup
python -m venv pyqt6-env
source pyqt6-env/bin/activate
pip install -r requirements.txt

# Windows virtual environment setup
python -m venv pyqt6-env
.\pyqt6-env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Usage
```bash
python main.py
```

### Recommended System Setup

For the best experience, use this application on laptops with screens larger than 11 inches (measured diagonally).

## Terms & Conditions

This application uses design elements licensed under Canva’s Free Content License and Adobe Stock’s Standard License. End users are not permitted to extract, reuse, modify, redistribute, or make separate use of visual content embedded in the app. By using this application, you agree not to attempt to access or repurpose any licensed media included herein.

Full license terms:
    <a href="https://www.canva.com/policies/content-license-agreement/">Canva License</a> ,
    <a href="https://www.adobe.com/content/dam/cc/en/legal/terms/enterprise/pdfs/PSLT-Stock-WW-2024v1.pdf">Adobe Stock License</a>

## Application Maintenance

### How do I compile main.py into an executable on Mac and Windows?

#### Windows
Enter the following in your terminal or IDE after entering the directory with your main.py file:

```bash

pyinstaller --noconfirm --windowed --onefile --icon="images/BEST_App_Logo.ico" main.py --add-data "images;images" --add-data "utils;utils" --add-data "pages;pages" --collect-submodules PyQt6

```

To delete the newly compiled Windows app:

```bash

Remove-Item -Recurse -Force build, dist, main.spec

```


#### Mac
Enter the following in your terminal or IDE after entering the directory with your main.py file:

```bash
pyinstaller --noconfirm --windowed --onefile --icon="images/BEST_App_Logo.icns" main.py --add-data "images:images" --add-data "utils:utils" --add-data "pages:pages" --collect-submodules PyQt6
```

To delete the newly compiled Mac app:

```bash

rm -rf build/ dist/ main.spec

```

### How do I make changes to the UI?

1. Open Qt Designer

```bash

pyqt6-tools designer 

```
2. Open .ui file
3. Make edits using Qt Designer interface
4. Save .ui file
5. Convert .ui to .py

```bash

pyuic6 0_main.ui -o 0_main_ui.py 

```
5. You're done!

### Why do Mac and Windows versions have a separate set of folders?

The Mac and Windows applications maintain distinct sets of folders due to differences in how their respective user interfaces are rendered. Consequently, the Windows version requires manual adjustments to ensure the UI is properly aligned and consistent.


