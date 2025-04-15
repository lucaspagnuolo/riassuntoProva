import time
import streamlit as st
from docx import Document
from mistralai.client import MistralClient

# API Key
api_key = st.secrets["kPt2yjT2ObCWWd5oL2hHtVHPcdGTAyAC"]
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
7. Indicazioni operative o esecutive

Sii chiaro, preciso e mantieni uno stile formale e professionale. Non tralasciare alcun dettaglio rilevante.
"""

    st.write("🧠 Sto generando il riassunto...")

    start_time = time.time()
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": full_text}
        ]
    )
    end_time = time.time()

    summary = response.choices[0].message.content

    st.success(f"✅ Riassunto completato in {((end_time - start_time) / 60):.2f} minuti")
    st.subheader("📄 Riassunto generato:")
    st.write(summary)

    # Esportazione DOCX
    output_doc = Document()
    output_doc.add_paragraph(summary)
    output_path = "Riassunto_Generato.docx"
    output_doc.save(output_path)

    with open(output_path, "rb") as file:
        st.download_button("📥 Scarica il riassunto", file, file_name="Riassunto_Generato.docx")
