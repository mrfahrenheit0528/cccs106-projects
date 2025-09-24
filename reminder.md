
# 🐍 CCCS 106 — Virtual Environment Best Practices

To keep your development environment consistent and error‑free throughout the semester, follow these guidelines for working with your **virtual environment**.

---

## 🔑 Workflow

- **Always activate** your environment before coding:
  ```powershell
  cccs106_env_hermoso\Scripts\activate
  ```

- **Use the same environment** for all modules and lab activities. This ensures your dependencies stay consistent across the course.

- **Deactivate when done**:
  ```powershell
  deactivate
  ```

---

## 📌 Maintenance Tips

- **Never delete** your `cccs106_env_lastname` folder during the semester.  
  If you accidentally remove it, you’ll need to rebuild and reinstall all dependencies.

- **Keep dependencies backed up**:  
  Update your `requirements.txt` whenever you install new packages:
  ```powershell
  pip freeze > requirements.txt
  ```

- **Rebuild on another machine** (e.g., laptop ↔ PC):
  ```powershell
  python -m venv cccs106_env_lastname
  .\cccs106_env_lastname\Scripts\activate
  pip install -r requirements.txt
  ```

---

## ⚠️ Critical Reminder

> You must use this **same virtual environment** for **all CCCS 106 work** throughout the semester.  
> Mixing environments or skipping activation will cause errors and inconsistencies.

