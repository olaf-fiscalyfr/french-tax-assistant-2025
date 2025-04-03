import streamlit as st
import pandas as pd
import json
import time
import io
import zipfile
import tempfile
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document
import extract_msg
import mailparser

st.set_page_config(page_title="🇫🇷 French Tax Assistant 2025", layout="centered")

# --- Sidebar instructions ---
with st.sidebar:
    st.title("📌 Instructions")
    st.markdown("""
    1. Upload your documents (PDF, Word, Excel, JSON, TXT, MSG, EML, ZIP)
    2. The assistant will extract relevant data
    3. Review the summary
    4. Download the final Excel file
    """)
    st.markdown("---")
    st.markdown("Made by Olaf @ Fiscalyfr")

st.title("🇫🇷 French Tax Assistant 2025")
st.markdown("Upload your client documents – the assistant will extract key tax data and generate an Excel summary for Clickimpôts.")

uploaded_files = st.file_uploader(
    "📁 Upload files (PDF, DOCX, XLSX, JSON, TXT, MSG, EML, ZIP)",
    type=["pdf", "docx", "xlsx", "json", "txt", "msg", "eml", "zip"],
    accept_multiple_files=True
)

entries = []

def parse_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def parse_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def parse_txt(file):
    try:
        return file.read().decode("utf-8")
    except UnicodeDecodeError:
        return file.read().decode("latin-1")

def parse_json(file):
    return json.dumps(json.load(file), indent=2)

def parse_xlsx(file):
    df = pd.read_excel(file)
    return df.to_string()

def parse_msg(file):
    msg = extract_msg.Message(file)
    return f"Subject: {msg.subject}\nBody:\n{msg.body}"

def parse_eml(file):
    email = mailparser.parse_from_bytes(file.read())
    return f"Subject: {email.subject}\nBody:\n{email.body}"

def parse_zip(file):
    with tempfile.TemporaryDirectory() as tmpdir:
        zf = zipfile.ZipFile(file)
        zf.extractall(tmpdir)
        for inner_path in Path(tmpdir).rglob("*"):
            if inner_path.is_file():
                ext = inner_path.suffix.lower().strip(".")
                with open(inner_path, "rb") as f:
                    try:
                        content = parse_file(f, ext)
                        entries.append({"filename": inner_path.name, "content": content})
                    except:
                        pass

def parse_file(file, ext):
    if ext == "pdf":
        return parse_pdf(file)
    elif ext == "docx":
        return parse_docx(file)
    elif ext == "txt":
        return parse_txt(file)
    elif ext == "json":
        return parse_json(file)
    elif ext == "xlsx":
        return parse_xlsx(file)
    elif ext == "msg":
        return parse_msg(file)
    elif ext == "eml":
        return parse_eml(file)
    return "Unsupported file"

if uploaded_files:
    with st.spinner("🔍 Extracting data..."):
        time.sleep(1)
        for file in uploaded_files:
            suffix = Path(file.name).suffix.lower().strip(".")
            if suffix == "zip":
                parse_zip(file)
            else:
                try:
                    content = parse_file(file, suffix)
                    entries.append({"filename": file.name, "content": content})
                except Exception as e:
                    entries.append({"filename": file.name, "content": f"Error reading file: {e}"})

    st.markdown("### 📄 Preview of Extracted Data")
    for entry in entries:
        st.subheader(entry["filename"])
        st.text(entry["content"][:1000])

    df = pd.DataFrame([
        {"Fichier": e["filename"], "Contenu": e["content"][:1000]} for e in entries
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Extraction", index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Report",
        data=output,
        file_name="declaration_clickimpots_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("⬆️ Upload documents to begin.")
