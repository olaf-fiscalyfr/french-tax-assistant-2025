import streamlit as st
import pandas as pd
import json
import time
from PyPDF2 import PdfReader
from docx import Document
from pathlib import Path
import io
from openai import OpenAI

# --- HARDCODED API KEY ---
OPENAI_API_KEY = "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"

# --- GPT extraction function ---
def extract_with_gpt(text):
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
You are a professional French tax assistant. Extract all tax-relevant information for the French income tax return for year 2024 from the following document.
Include:
- Revenus fonciers, mobiliers, salaires, pensions, dividendes
- Intérêts bancaires (Livret A, LEP, etc.)
- Comptes bancaires étrangers (form 3916)
- Locations meublées (form 2042-C PRO / 2031)
- Revenus étrangers (form 2047)
- Micro-entrepreneur chiffre d'affaires
- All codes (e.g., 1AJ, 2TR, 8TK, 5HY, 7UF, etc.)

Return a structured JSON with:
1. Data grouped by form (2042, 2044, 2047, 2042-C PRO, 3916, etc.)
2. A `summary` array with:
  - form
  - code
  - description
  - amount (number in euros)

IMPORTANT:
- Return only valid JSON
- If a value is missing or unknown, write "MISSING"
- Do NOT return markdown or any explanation

Document content:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts French tax data."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
    )

    return response.choices[0].message.content

# --- Split text into overlapping chunks ---
def split_text_into_chunks(text, size=3000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start+size])
        start += size - overlap
    return chunks

# --- Flatten GPT JSON output for Excel ---
def flatten_tax_json(tax_json):
    rows = []
    summary = tax_json.pop("summary", [])
    for item in summary:
        rows.append({
            "Formulaire": item.get("form"),
            "Code": item.get("code"),
            "Description": item.get("description"),
            "Montant": item.get("amount")
        })
    return pd.DataFrame(rows), tax_json

# --- Streamlit UI ---
st.title("🇫🇷 Assistant Fiscal GPT - Déclaration de Revenus 2024")
st.markdown("Analysez automatiquement les documents fiscaux de vos clients pour 2024 et préparez un fichier pour Clickimpôts.")

uploaded_files = st.file_uploader(
    "📄 Déposez vos documents ici (PDF, DOCX, TXT, JSON)",
    type=["pdf", "docx", "txt", "json"],
    accept_multiple_files=True
)

all_text = ""

if uploaded_files:
    st.info("📚 Traitement des documents...")
    for file in uploaded_files:
        suffix = Path(file.name).suffix.lower()

        if suffix == ".pdf":
            reader = PdfReader(file)
            all_text += "\n".join(page.extract_text() or "" for page in reader.pages)

        elif suffix == ".docx":
            doc = Document(file)
            all_text += "\n".join(para.text for para in doc.paragraphs)

        elif suffix == ".txt":
            all_text += file.read().decode("utf-8", errors="ignore")

        elif suffix == ".json":
            content = json.load(file)
            all_text += json.dumps(content, indent=2)

    with st.spinner("💬 Extraction des données avec GPT-4..."):
        try:
            chunks = split_text_into_chunks(all_text)
            merged_summary = []
            merged_forms = {}

            for i, chunk in enumerate(chunks):
                st.info(f"📄 Analyse du segment {i+1}/{len(chunks)}...")
                gpt_raw_result = extract_with_gpt(chunk)
                st.code(gpt_raw_result, language="json")

                if gpt_raw_result.strip().startswith("{"):
                    try:
                        parsed_result = json.loads(gpt_raw_result)
                    except json.JSONDecodeError:
                        st.warning(f"⚠️ Chunk {i+1} non parsable.")
                        continue

                    summary = parsed_result.pop("summary", [])
                    merged_summary.extend(summary)

                    for form, fields in parsed_result.items():
                        if form not in merged_forms:
                            merged_forms[form] = {}
                        if isinstance(fields, dict):
                            for k, v in fields.items():
                                if isinstance(v, dict) and "code" in v and "amount" in v:
                                    merged_forms[form][v["code"]] = v["amount"]
                                elif isinstance(v, dict) and len(v) == 1 and isinstance(list(v.values())[0], dict):
                                    inner = list(v.values())[0]
                                    merged_forms[form][inner.get("code", k)] = inner.get("amount", "MISSING")
                                else:
                                    merged_forms[form][k] = v
                        elif isinstance(fields, list):
                            for item in fields:
                                code = item.get("code") or item.get("label") or f"UNKNOWN_{len(merged_forms[form])}"
                                value = item.get("value") or item.get("amount") or "0"
                                merged_forms[form][code] = value
                        else:
                            st.warning(f"⚠️ Le formulaire {form} contient un format inattendu.")

            if not merged_summary:
                st.error("❌ Aucun champ fiscal détecté dans les documents fournis.")
                st.stop()

            df_summary = pd.DataFrame([{
                "Formulaire": item.get("form"),
                "Code": item.get("code"),
                "Description": item.get("description"),
                "Montant": item.get("amount")
            } for item in merged_summary])

            # Filter out rows with missing or empty values
            df_summary = df_summary[df_summary["Montant"].notna() & (df_summary["Montant"] != "MISSING")]

            st.success("✅ Extraction réussie")
            st.subheader("🧾 Synthèse pour Clickimpôts")
            st.dataframe(df_summary)

            # Export Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_summary.to_excel(writer, sheet_name="2024", index=False)
                for form, fields in merged_forms.items():
                    df = pd.DataFrame([{"Code": k, "Valeur": v} for k, v in fields.items() if v not in [None, "MISSING"]])
                    df.to_excel(writer, sheet_name=form[:30], index=False)
            output.seek(0)

            st.download_button(
                label="📥 Télécharger le fichier Clickimpôts (Excel)",
                data=output,
                file_name="clickimpots_2024_gpt.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Export JSON for Clickimpots
            clickimpots_data = []
            for _, row in df_summary.iterrows():
                clickimpots_data.append({
                    "form": row["Formulaire"],
                    "code": row["Code"],
                    "value": row["Montant"]
                })

            json_output = json.dumps(clickimpots_data, indent=2, ensure_ascii=False).encode("utf-8")

            st.download_button(
                label="📄 Télécharger Clickimpôts JSON",
                data=json_output,
                file_name="clickimpots_2024.json",
                mime="application/json"
            )

        except Exception as e:
            st.error(f"❌ Erreur d'analyse GPT : {e}")
else:
    st.info("🧾 Veuillez charger un ou plusieurs fichiers pour commencer.")
