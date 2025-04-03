import streamlit as st
import pandas as pd
import json
import time
import openai
from PyPDF2 import PdfReader
from docx import Document
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
    "📄 Drop your files here", 
    type=["pdf", "docx", "txt", "json"], 
    accept_multiple_files=True
)

data_entries = []
json_data = {}

def extract_with_gpt(text, api_key):
    openai.api_key = api_key
    prompt = f"""
You are a French tax assistant. Extract relevant tax data from the following document text and format it by French tax form (e.g., 2042, 2047, 2086, 3916). Use JSON format like:
{{
  "2042": {{
    "1AJ": "X €",
    "1BZ": "Y €"
  }},
  "2047": {{
    "revenus_etrangers": "Z €"
  }}
}}

Document content:
{text[:3000]}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000,
    )
    return response.choices[0].message["content"]

if uploaded_files:
    with st.spinner("🔍 Analyzing documents..."):
        time.sleep(1)

        for file in uploaded_files:
            filename = file.name
            suffix = Path(filename).suffix.lower()

            if suffix == ".json":
                json_data = json.load(file)
                st.success(f"🧐 JSON loaded: {filename}")

            elif suffix == ".pdf":
                reader = PdfReader(file)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                data_entries.append({"filename": filename, "text": text})
                st.success(f"📄 PDF loaded: {filename}")

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
                data_entries.append({"filename": filename, "text": raw})
                st.success(f"📝 Text file loaded: {filename}")

    # --- Preview extracted text ---
    st.markdown("### 📊 Extracted Data (Preview)")
    for entry in data_entries:
        st.subheader(entry["filename"])
        st.text(entry["text"][:1000])  # First 1000 chars

    # --- GPT Extraction ---
    st.markdown("---")
    st.header("🧠 Extract tax data with GPT-4")
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    selected_file = st.selectbox("Select a document to extract from", [e["filename"] for e in data_entries])
    extract_button = st.button("Run GPT-4 Extraction")

    if extract_button and api_key:
        selected_text = next(e["text"] for e in data_entries if e["filename"] == selected_file)
        with st.spinner("Talking to GPT-4..."):
            try:
                gpt_result = extract_with_gpt(selected_text, api_key)
                st.success("✅ Extraction complete")
                st.code(gpt_result, language="json")
            except Exception as e:
                st.error(f"❌ GPT-4 extraction failed: {e}")

    # --- Export to Excel ---
    df = pd.DataFrame([
        {"Fichier": e["filename"], "Type": Path(e["filename"]).suffix.upper(), "Montant": "To be extracted"}
        for e in data_entries
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="2042", index=False)
    output.seek(0)

    st.download_button(
        label="📅 Download Clickimpôts Excel",
        data=output,
        file_name="declaration_clickimpots_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("⬆️ Upload a file to get started.")
