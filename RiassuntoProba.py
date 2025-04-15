import streamlit as st
import time
from mistralai import Mistral
from spire.doc import *
from spire.doc.common import *

# Impostazioni API
api_key = "kPt2yjT2ObCWWd5oL2hHtVHPcdGTAyAC"
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

# Funzione per generare il riassunto
def generate_summary(document_path):
    doc = Document()
    doc.LoadFromFile(document_path)
    text = doc.GetText()

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

    start_time = time.time()

    response = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": text}
        ]
    )

    summary = response.choices.message.content
    end_time = time.time()
    elapsed_minutes = (end_time - start_time) / 60

    return summary, elapsed_minutes

# Streamlit app
st.title("Generatore di Riassunti per Documenti Complessi")

uploaded_file = st.file_uploader("Carica un documento Word", type=["docx"])

if uploaded_file is not None:
    with open("uploaded_document.docx", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("Documento caricato con successo!")

    if st.button("Genera Riassunto"):
        summary, elapsed_minutes = generate_summary("uploaded_document.docx")
        
        st.write(f"Riassunto completato in {elapsed_minutes:.2f} minuti.")
        st.write(summary)

        # Salva il riassunto in un nuovo documento Word
        output_doc = Document()
        section = output_doc.AddSection()
        paragraph = section.AddParagraph()
        paragraph.AppendText(summary)

        output_file = "Capitolato_Oneri_Riassunto.docx"
        output_doc.SaveToFile(output_file, FileFormat.Docx)

        with open(output_file, "rb") as f:
            st.download_button(
                label="Scarica il riassunto",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
