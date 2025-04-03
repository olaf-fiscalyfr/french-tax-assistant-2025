import streamlit as st
import pandas as pd
import json
import time
from PyPDF2 import PdfReader
<<<<<<< HEAD
=======
from docx import Document
>>>>>>> a06ba87f1f10134ab3c57fb44e2961897e6278f9
from pathlib import Path
import io

st.set_page_config(page_title="🇫🇷 French Tax Assistant 2025", layout="centered")

# --- Sidebar instructions ---
with st.sidebar:
    st.title("📌 Instructions")
    st.markdown("""
    1. Upload your PDF, DOCX, or JSON file  
    2. GPT-4 analyzes the content  
    3. Review extracted data  
    4. Download the Excel file  
    """)
    st.markdown("---")
    st.markdown("Made by Olaf @ Fiscalyfr")

# --- Main header ---
st.title("🇫🇷 French Tax Assistant 2025")
st.markdown("Upload client tax documents and generate a Clickimpôts-ready Excel file.")

# --- File upload ---
uploaded_files = st.file_uploader(
<<<<<<< HEAD
    "📤 Drop your files here", 
    type=["pdf", "docx", "json"], 
=======
    "📄 Drop your files here", 
    type=["pdf", "docx", "txt", "json"], 
>>>>>>> a06ba87f1f10134ab3c57fb44e2961897e6278f9
    accept_multiple_files=True
)

# --- File parsing + mock output ---
data_entries = []
json_data = {}

if uploaded_files:
    with st.spinner("🔍 Analyzing documents..."):
        time.sleep(1)

        for file in uploaded_files:
            filename = file.name
            suffix = Path(filename).suffix.lower()

            if suffix == ".json":
                json_data = json.load(file)
<<<<<<< HEAD
                st.success(f"🧠 JSON loaded: {filename}")
=======
                st.success(f"🧐 JSON loaded: {filename}")
>>>>>>> a06ba87f1f10134ab3c57fb44e2961897e6278f9

            elif suffix == ".pdf":
                reader = PdfReader(file)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                data_entries.append({"filename": filename, "text": text})
                st.success(f"📄 PDF loaded: {filename}")

<<<<<<< HEAD
            elif suffix in [".docx", ".txt"]:
                raw = file.read().decode("utf-8")
=======
            elif suffix == ".docx":
                try:
                    doc = Document(file)
                    raw = "\n".join([para.text for para in doc.paragraphs])
                    st.success(f"📃 Word document loaded: {filename}")
                except Exception as e:
                    st.error(f"❌ Failed to read DOCX file: {filename}\n{e}")
                    raw = ""
                data_entries.append({"filename": filename, "text": raw})

            elif suffix == ".txt":
                file_bytes = file.read()
                try:
                    raw = file_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    raw = file_bytes.decode("latin-1")
                    st.warning(f"⚠️ {file.name} was decoded with fallback encoding (latin-1)")

>>>>>>> a06ba87f1f10134ab3c57fb44e2961897e6278f9
                data_entries.append({"filename": filename, "text": raw})
                st.success(f"📝 Text file loaded: {filename}")

    # --- Display preview ---
    st.markdown("### 📊 Extracted Data (Preview)")
    for entry in data_entries:
        st.subheader(entry["filename"])
        st.text(entry["text"][:1000])  # First 1000 chars

    # --- Export to Excel ---
<<<<<<< HEAD
    df = pd.DataFrame([{"Fichier": e["filename"], "Type": "PDF", "Montant": "To be extracted"} for e in data_entries])
=======
    df = pd.DataFrame([
        {"Fichier": e["filename"], "Type": Path(e["filename"]).suffix.upper(), "Montant": "To be extracted"}
        for e in data_entries
    ])
>>>>>>> a06ba87f1f10134ab3c57fb44e2961897e6278f9
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="2042", index=False)
    output.seek(0)

    st.download_button(
<<<<<<< HEAD
        label="📥 Download Clickimpôts Excel",
=======
        label="📅 Download Clickimpôts Excel",
>>>>>>> a06ba87f1f10134ab3c57fb44e2961897e6278f9
        data=output,
        file_name="declaration_clickimpots_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

<<<<<<< HEAD
elif not uploaded_files:
    st.info("⬆️ Upload a file to get started.")
=======
else:
    st.info("⬆️ Upload a file to get started.")
>>>>>>> a06ba87f1f10134ab3c57fb44e2961897e6278f9
