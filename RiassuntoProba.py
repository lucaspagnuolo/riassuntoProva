import streamlit as st
from mistralai import Mistral
from docx import Document
import tempfile
import os

st.set_page_config(page_title="Riassunto Documento", layout="centered")
st.title("📝 Riassunto dettagliato documento Word")

# 1. Inserisci la chiave API
api_key = st.text_input("🔑 Inserisci la tua Mistral API Key:", type="password")

# 2. Carica file Word
uploaded_file = st.file_uploader("📁 Carica un file Word (.docx)", type=["docx"])

if api_key and uploaded_file:
    if st.button("📚 Genera Riassunto"):
        with st.spinner("⏳ Elaborazione in corso..."):

            # Salva temporaneamente il file Word caricato
            temp_input_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.read())

            # Estrai testo dal file .docx con python-docx
            doc = Document(temp_input_path)
            testo = "\n".join([para.text for para in doc.paragraphs])

            # Prompt per Mistral
            system_prompt = """
Sei un assistente legale esperto in lettura documentale. Riceverai il testo di un documento Word (potenzialmente complesso o tecnico). Il tuo compito è produrre un **riassunto dettagliato** e preciso dell'intero contenuto, mantenendo i punti salienti, la struttura logica e gli aspetti principali. 
Mantieni lo stile formale. Se possibile, suddividi il riassunto in **punti elenco o sezioni tematiche** (ad esempio: Oggetto, Finalità, Durata, Obblighi, Requisiti, ecc.).
"""

            # Chiamata al modello Mistral
            client = Mistral(api_key=api_key)
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": testo}
                ]
            )
            riassunto = response.choices[0].message.content

            # Mostra anteprima formattata
            st.subheader("👀 Anteprima del Riassunto")
            st.markdown(f"<div style='white-space: pre-wrap; font-family:monospace;'>{riassunto}</div>", unsafe_allow_html=True)

            # Crea file Word per download con python-docx
            output_doc = Document()
            output_doc.add_paragraph(riassunto)

            output_path = os.path.join(tempfile.gettempdir(), "riassunto.docx")
            output_doc.save(output_path)

            # Bottone per scaricare
            with open(output_path, "rb") as f:
                st.download_button("📥 Scarica Riassunto in .docx", f, file_name="riassunto.docx")
else:
    st.info("Inserisci la chiave API e carica un file Word per procedere.")
