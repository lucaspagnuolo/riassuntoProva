import streamlit as st
import requests
from spire.doc import Document
from spire.doc.common import FileFormat
import tempfile
import os

st.set_page_config(page_title="Riassunto Documento", layout="centered")
st.title("📝 Riassunto dettagliato documento Word")

# 1. Inserisci la chiave API
api_key = st.text_input("🔑 Inserisci la tua Mistral API Key:", type="password")

# 2. Carica file Word
uploaded_file = st.file_uploader("📁 Carica un file Word (.docx)", type=["docx"])

def get_summary_mistral(api_key, system_prompt, user_text):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

if api_key and uploaded_file:
    if st.button("📚 Genera Riassunto"):
        with st.spinner("⏳ Elaborazione in corso..."):

            # Salva temporaneamente il file Word caricato
            temp_input_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.read())

            # Estrai testo dal .docx
            doc = Document()
            doc.LoadFromFile(temp_input_path)
            testo = doc.GetText()

            # Prompt per Mistral
            system_prompt = """
Sei un assistente legale esperto in lettura documentale. Riceverai il testo di un documento Word (potenzialmente complesso o tecnico). Il tuo compito è produrre un **riassunto dettagliato** e preciso dell'intero contenuto, mantenendo i punti salienti, la struttura logica e gli aspetti principali. 
Mantieni lo stile formale. Se possibile, suddividi il riassunto in **punti elenco o sezioni tematiche** (ad esempio: Oggetto, Finalità, Durata, Obblighi, Requisiti, ecc.).
"""

            try:
                riassunto = get_summary_mistral(api_key, system_prompt, testo)

                # Mostra anteprima formattata
                st.subheader("👀 Anteprima del Riassunto")
                st.markdown(f"<div style='white-space: pre-wrap; font-family:monospace;'>{riassunto}</div>", unsafe_allow_html=True)

                # Crea file Word per download
                output_doc = Document()
                section = output_doc.AddSection()
                paragraph = section.AddParagraph()
                paragraph.AppendText(riassunto)

                output_path = os.path.join(tempfile.gettempdir(), "riassunto.docx")
                output_doc.SaveToFile(output_path, FileFormat.Docx)

                # Bottone per scaricare
                with open(output_path, "rb") as f:
                    st.download_button("📥 Scarica Riassunto in .docx", f, file_name="riassunto.docx")

            except Exception as e:
                st.error(f"Errore durante la generazione del riassunto: {e}")
else:
    st.info("Inserisci la chiave API e carica un file Word per procedere.")
