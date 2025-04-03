# 🇫🇷 French Tax Assistant 2025 – Clickimpôts

An intelligent assistant to automatically extract tax data from client documents (PDF, Word, JSON) and generate an Excel file ready to import into Clickimpôts.

## 🔧 Features

- Upload PDF / Word / JSON documents
- Automatic extraction powered by GPT-4 (API key required)
- Editable table for manual corrections
- Generates a structured Excel file with tax forms:
  - 2042, 2044, 2047, 2086, 3916

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
