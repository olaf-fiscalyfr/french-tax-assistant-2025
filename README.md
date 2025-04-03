# 🇫🇷 Assistant Déclaration Fiscale 2025 – Clickimpôts

Un assistant intelligent pour extraire automatiquement les données fiscales des documents clients (PDF, Word, JSON) et générer un fichier Excel prêt à importer dans Clickimpôts.

## 🔧 Fonctionnalités
- Téléversement de documents PDF / Word / JSON
- Extraction automatique avec GPT-4 (clé API requise)
- Tableau éditable pour correction manuelle
- Génération d’un fichier Excel structuré avec les formulaires :
  - 2042, 2044, 2047, 2086, 3916

## 🚀 Lancer localement

```bash
pip install -r requirements.txt
streamlit run app.py