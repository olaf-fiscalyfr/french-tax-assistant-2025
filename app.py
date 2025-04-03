# app.py
import streamlit as st
import pandas as pd
import os
import tempfile
import json
import io
from pathlib import Path

# Document parsing imports
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import textract
import pdfplumber
from PIL import Image
import pytesseract

st.set_page_config(page_title="🇫🇷 French Tax Assistant 2025", layout="centered")

st.title("🇫🇷 French Tax Assistant 2025")
st.markdown("Drop your tax documents to extract totals and generate a Clickimpôts-ready Excel file.")

uploaded_files = st.file_uploader("Upload files (PDF, DOCX, TXT, JSON, MSG, Excel)",
                                   type=["pdf", "docx", "txt", "json", "msg", "xlsx"],
                                   accept_multiple_files=True)

extracted_texts = []

# --- Utility functions ---
def extract_text_from_pdfplumber(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_pdf(file):
    try:
        return extract_text_from_pdfplumber(file)
    except:
        try:
            reader = PdfReader(file)
            return "\n".join([p.extract_text() or "" for p in reader.pages])
        except:
            return ""

def extract_text_from_docx(file):
    try:
        doc = DocxDocument(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except:
        return ""

def extract_text_from_txt(file):
    try:
        return file.read().decode("utf-8")
    except UnicodeDecodeError:
        return file.read().decode("latin-1")

def extract_text_from_ocr(file):
    try:
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    except:
        return ""

def extract_text_with_textract(path):
    try:
        return textract.process(path).decode("utf-8")
    except:
        return ""

# --- Extraction process ---
if uploaded_files:
    for file in uploaded_files:
        filename = file.name
        suffix = Path(filename).suffix.lower()
        raw_text = ""

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        if suffix == ".pdf":
            raw_text = extract_text_from_pdf(tmp_path)
        elif suffix == ".docx":
            raw_text = extract_text_from_docx(tmp_path)
        elif suffix == ".txt":
            raw_text = extract_text_from_txt(file)
        elif suffix == ".json":
            with open(tmp_path, "r") as jf:
                json_obj = json.load(jf)
                raw_text = json.dumps(json_obj, indent=2)
        elif suffix in [".msg", ".eml"]:
            raw_text = extract_text_with_textract(tmp_path)
        elif suffix in [".jpg", ".jpeg", ".png"]:
            raw_text = extract_text_from_ocr(tmp_path)
        elif suffix in [".xls", ".xlsx"]:
            df = pd.read_excel(tmp_path)
            raw_text = df.to_string()

        extracted_texts.append({"filename": filename, "text": raw_text})

    st.markdown("## 📊 Extracted Document Previews")
    for entry in extracted_texts:
        st.subheader(entry["filename"])
        st.text(entry["text"][:1000])

    # --- Simulated totals (to be replaced by GPT-based analysis) ---
    df_out = pd.DataFrame([
        {"Formulaire": "2042", "Case": "1AJ", "Montant": 12000},
        {"Formulaire": "2047", "Case": "8TK", "Montant": 5500},
        {"Formulaire": "2086", "Case": "3VG", "Montant": 3100},
    ])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name="2042")
    output.seek(0)

    st.download_button(
        label="📅 Download Clickimpôts Excel",
        data=output,
        file_name="declaration_clickimpots_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
