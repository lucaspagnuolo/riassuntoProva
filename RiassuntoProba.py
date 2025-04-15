import time
import streamlit as st
from docx import Document  # Usa python-docx per leggere file .docx
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Impostazioni API
api_key = st.secrets["MISTRAL_API_KEY"]
model = "mistral-large-latest"  # Puoi cambiare il modello se ne usi un altro

client = MistralClient(api_key=api_key)

# Interfaccia Streamlit
st.set_page_config(page_title="Riassunto Capitolato", page_icon="📄")
st.title("📄 Riassunto Automatico di un Capitolato")
st.write("Carica un file .docx per generare un riassunto con l'AI.")

uploaded_file = st.file_uploader("Carica un file .docx", type="docx")

if uploaded_file:
    # Caricamento file
    doc = Document(uploaded_file)
    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])

    # Mostra anteprima
    with st.expander("📃 Anteprima del contenuto"):
        st.text(full_text[:3000] + ("..." if len(full_text) > 3000 else ""))

    # Prompt per riassunto
    summary_prompt = "Sei un assistente specializzato in appalti pubblici. Riassumi il seguente capitolato in modo chiaro ed esaustivo:"

    # Esecuzione con modello Mistral
    with st.spinner("Sto generando il riassunto..."):
        response = client.chat(
            model=model,
            messages=[
                ChatMessage(role="system", content=summary_prompt),
                ChatMessage(role="user", content=full_text)
            ]
        )
        summary = response.choices[0].message.content

    st.subheader("✍️ Riassunto Generato:")
    st.write(summary)
