import streamlit as st
import time
from mistralai import Mistral
from spire.doc import *
from spire.doc.common import *

# Impostazioni API con chiave presa dai secrets
try:
    api_key = st.secrets["MISTRAL_API_KEY"]
except KeyError:
    st.error("❌ Chiave API non trovata nei secrets. Assicurati di averla inserita correttamente nei settings di Streamlit.")
    st.stop()

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

    try:
        summary = response.choices[0].message.content
    except Exception as e:
        summary = f"Errore nella generazione del riassunto: {str(e)}"

    end_time = time.time()
    elapsed_minutes = (end_time - start_time) / 60

    return summary, text, elapsed_minutes


# Streamlit app
st.title("📝 Generatore di Riassunti per Documenti Complessi + Chat")

uploaded_file = st.file_uploader("📤 Carica un documento Word", type=["docx"])

if uploaded_file is not None:
    with open("uploaded_document.docx", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("✅ Documento caricato con successo!")

    if st.button("🧠 Genera Riassunto"):
        with st.spinner("📚 Analisi del documento in corso..."):
            summary, text, elapsed_minutes = generate_summary("uploaded_document.docx")
            st.session_state["document_text"] = text  # salva il testo per la chat

        st.success(f"✅ Riassunto completato in {elapsed_minutes:.2f} minuti.")

        # Mostra l'anteprima del riassunto
        st.subheader("📄 Anteprima del Riassunto")
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
                label="📥 Scarica il riassunto",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # Sezione per la chat interattiva sul documento
    if "document_text" in st.session_state:
        st.divider()  # Separatore per la sezione della chat
        st.subheader("💬 Chatta con l'Assistente del Documento")

        user_question = st.text_input("Fai una domanda sul contenuto del documento")

        if user_question:
            with st.spinner("🧾 Sto leggendo il documento per risponderti..."):
                chat_response = client.chat.complete(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Rispondi in modo chiaro, preciso e professionale basandoti solo sul testo del documento."},
                        {"role": "user", "content": f"Testo del documento:\n\n{st.session_state['document_text']}\n\nDomanda: {user_question}"}
                    ]
                )
                answer = chat_response.choices[0].message.content
                st.markdown(f"**Risposta:** {answer}")
