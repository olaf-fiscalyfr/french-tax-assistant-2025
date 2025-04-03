import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path
import pdfplumber
from docx import Document
from PIL import Image
import io

st.set_page_config(page_title="🇫🇷 French Tax Assistant 2025", layout="centered")

# --- Sidebar instructions ---
with st.sidebar:
    st.title("📌 Instructions")
    st.markdown("""
    1. Upload your PDF, DOCX, TXT or JSON files  
    2. The app extracts key data  
    3. You review and download the Excel  
    """)
    st.markdown("---")
    st.markdown("Made by Olaf @ Fiscalyfr")

# --- Main header ---
st.title("🇫🇷 French Tax Assistant 2025")
st.markdown("Upload tax docs and generate an Excel file for Clickimpôts.")

# --- Upload section ---
uploaded_files = st.file_uploader(
    "📁 Drop your files here",
    type=["pdf", "docx", "txt", "json"],
    accept_multiple_files=True
)

data_entries = []

if uploaded_files:
    with st.spinner("🔍 Analyzing documents..."):
        time.sleep(1)

        for file in uploaded_files:
            filename = file.name
            suffix = Path(filename).suffix.lower()
            raw_text = ""

            if suffix == ".pdf":
                try:
                    with pdfplumber.open(file) as pdf:
                        raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    st.success(f"📄 PDF loaded: {filename}")
                except Exception as e:
                    st.error(f"❌ Could not read PDF: {filename}\n{e}")

            elif suffix == ".docx":
                try:
                    doc = Document(file)
                    raw_text = "\n".join([para.text for para in doc.paragraphs])
                    st.success(f"📃 Word document loaded: {filename}")
                except Exception as e:
                    st.error(f"❌ Could not read DOCX: {filename}\n{e}")

            elif suffix == ".txt":
                try:
                    raw_text = file.read().decode("utf-8")
                except UnicodeDecodeError:
                    raw_text = file.read().decode("latin-1")
                    st.warning(f"⚠️ {filename} was decoded with fallback encoding (latin-1)")
                st.success(f"📝 Text file loaded: {filename}")

            elif suffix == ".json":
                try:
                    json_data = json.load(file)
                    raw_text = json.dumps(json_data, indent=2)
                    st.success(f"🧠 JSON file loaded: {filename}")
                except Exception as e:
                    st.error(f"❌ Could not read JSON: {filename}\n{e}")

            if raw_text:
                data_entries.append({"filename": filename, "text": raw_text})

    # --- Preview text ---
    st.markdown("### 📑 Preview extracted content")
    for entry in data_entries:
        st.subheader(entry["filename"])
        st.text(entry["text"][:1000])  # show first 1000 chars

    # --- Generate Excel mock ---
    df = pd.DataFrame([
        {
            "Fichier": e["filename"],
            "Type": Path(e["filename"]).suffix.upper(),
            "Montant estimé": "à extraire"
        }
        for e in data_entries
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="2042")
    output.seek(0)

    st.download_button(
        label="📥 Télécharger le fichier Excel",
        data=output,
        file_name="declaration_clickimpots_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("⬆️ Upload a file to get started.")
