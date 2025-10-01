# CCCS106 Projects — Workspace Overview

A collection of lab projects for CCCS106 (Application Development and Emerging Technologies). This repo contains Python and Flet GUI projects organized by week. This README describes the folder layout, requirements, and how to run each project's examples.

Quick introduction
- Purpose: store weekly lab code (Python scripts, Flet GUI apps), reports and build artifacts for CCCS106.
- Location: root of the workspace contains per-week folders: week1_labs, week2_labs, week3_labs, week4_labs.

Workspace layout (folders and purpose)
- week1_labs — basic Python exercises (hello_world.py, basic_calculator.py, LAB1_REPORT.md)
- week2_labs — Flet GUI examples (hello_flet.py, personal_info_gui.py, lab2_report.md)
- week3_labs — Login form example (Flet app + MySQL connector; db_connection.py, main.py)
- week4_labs — Contact Book App (Flet + sqlite) under contact_book_app/src
- Other files: requirements.txt, per-project pyproject.toml, and README files inside week folders.

Requirements
- Python 3.9+ (recommended: 3.9 — 3.12). Use a virtual environment.
- Flet 0.28.3 (used by the labs)
- For week3_labs (Login form) you need MySQL server and mysql-connector-python if you use that example.
- No global install required if you use a venv or Poetry.

Recommended quick setup (Windows)
1. Create and activate venv
2. Install dependencies:
   - pip install -r requirements.txt
3. Run a Flet app:
   - python path\to\app.py
   - or use the flet CLI: flet run path\to\app.py

How to run each week's projects (concise)

- week1_labs (pure Python)
  - Run scripts directly in the activated environment:
    - python week1_labs\hello_world.py
    - python week1_labs\basic_calculator.py

- week2_labs (Flet GUI)
  - Run with Python:
    - python week2_labs\hello_flet.py
    - python week2_labs\personal_info_gui.py
  - Or with flet CLI:
    - flet run week2_labs\hello_flet.py

- week3_labs (Login form + MySQL)
  - Prerequisite: MySQL server running and a database named per db_connection.py (default: host=localhost, user=root, password= , database=fletapp).
  - Update connection details in week3_labs\src\db_connection.py if needed.
  - Run:
    - python week3_labs\src\main.py
  - If using mysql-connector, ensure it is installed: pip install mysql-connector-python

- week4_labs (Contact Book App — sqlite)
  - No external DB required (uses sqlite).
  - From project root run:
    - python week4_labs\contact_book_app\src\main.py
  - The app will create contacts.db in the working directory.

Tips & notes
- Use the correct Python interpreter in your editor (VS Code: “Python: Select Interpreter”).
- For GUI reloading: stop and re-run the Python process after code changes.
- Keep credentials out of the repo (edit db_connection.py locally or use environment variables in real projects).

Troubleshooting
- If Flet window does not open, ensure your environment has Flet installed and the script uses ft.app(target=main).
- For MySQL connection issues, confirm server status and credentials; check firewall settings.