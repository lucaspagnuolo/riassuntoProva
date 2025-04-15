import time
import streamlit as st
from docx import Document
from mistralai.client import MistralClient

# API Key
api_key = st.secrets["MISTRAL_API_KEY"]
model = "mistral-large-latest"
client = MistralClient(api_key=api_key)

# Streamlit UI
st.title("📝 Riassunto automatico da documento Word")
uploaded_file = st.file_uploader("📂 Carica un file Word (.docx)", type=["docx"])

if uploaded_file is not None:
    # Lettura documento Word
    doc = Document(uploaded_file)
    full_text = "\n".join([para.text for para in doc.paragraphs])

    # Prompt per il modello
    summary_prompt = """
Sei un assistente altamente qualificato con esperienza in sintesi professionali di documenti complessi come capitolati, bandi di gara o documenti tecnici.

Il tuo compito è leggere il testo del documento e generare un riassunto dettagliato e strutturato. Il riassunto deve includere:

1. Obiettivo del documento
2. Contesto generale
3. Punti chiave e responsabilità
4. Scadenze, vincoli temporali e condizioni
5. Eventuali riferimenti a normative, leggi o regolamenti
6. Allegati o riferimenti a sezioni collegate
7. Indicazioni operative o esecut
