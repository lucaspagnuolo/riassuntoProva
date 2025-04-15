import time
import streamlit as st
from mistralai import Mistral
from docx import Document  # Usa python-docx al posto di spire.doc

# Impostazioni API
api_key = st.text_input("🔑 Inserisci la tua Mistral API Key:", type="password")
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

# Titolo dell'app
st.title("📝 Generatore di Riassunto Documenti Word")

# Selezione file da caricare
uploaded_file = st.file_uploader("📁 Carica un file Word (.docx)", type=["docx"])

if api_key and uploaded_file:
    if st.button("📚 Genera Riassunto"):
        with st.spinner("⏳ Elaborazione in corso..."):

            # Salva il file Word caricato in un file temporaneo
            with open("temp_documento.docx", "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Carica il documento con python-docx
            doc = Document("temp_documento.docx")
            text = "\n".join([para.text for para in doc.paragraphs])

            # Prompt unico per il riassunto
            summary_prompt = """
Sei un assistente altamente qualificato con esperienza in sintesi professionali di documenti complessi come capitolati, bandi di gara o documenti tecnici.

Il tuo compito è leggere il testo del documento e generare un riassunto dettagliato e strutturato. Il riassunto deve includere:

1. **Obiettivo del documento**
2. **Contesto generale**
3. **Punti chiave e responsabilità**
4. **Scadenze, vincoli temporali e condizioni**
5. **Eventuali riferimenti a normative, leggi o regolamenti**
6. **Allegati o riferimenti a sezioni collegate**
7. **Indicazioni operative o esecutive**

Sii chiaro, preciso e mantieni uno stile formale e professionale. Non tralasciare alcun dettaglio rilevante.
"""

            # Misura il tempo
            start_time = time.time()

            # Invio al modello Mistral
            response = client.chat.complete(
                model=model,
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": text}
                ]
            )

            summary = response.choices[0].message.content
            end_time = time.time()
            elapsed_minutes = (end_time - start_time) / 60

            st.subheader("👀 Anteprima del Riassunto")
            st.markdown(f"<div style='white-space: pre-wrap; font-family:monospace;'>{summary}</div>", unsafe_allow_html=True)

            st.write(f"Riassunto completato in {elapsed_minutes:.2f} minuti.")

            # Crea un nuovo documento Word con il riassunto
            output_doc = Document()
            section = output_doc.add_paragraph(summary)

            # Percorso di salvataggio del file di riassunto
            output_file = "riassunto_documento.docx"
            output_doc.save(output_file)

            # Bottone per scaricare il riassunto
            with open(output_file, "rb") as f:
                st.download_button("📥 Scarica Riassunto in .docx", f, file_name=output_file)

else:
    st.info("Inserisci la chiave API e carica un file Word per procedere.")
