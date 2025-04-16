import streamlit as st
from mistralai import Mistral
from docx import Document
import time
import fitz  # PyMuPDF

# Carica chiave API Mistral
try:
    api_key = st.secrets["MISTRAL_API_KEY"]
except KeyError:
    st.error("❌ Chiave API non trovata nei secrets.")
    st.stop()

model = "mistral-large-latest"
client = Mistral(api_key=api_key)

# Funzione per estrarre testo da PDF
def estrai_testo_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    testo = ""
    for page in doc:
        testo += page.get_text()
    return testo

# Funzione per generare bollettino da testo
def genera_bollettino_da_testo(testo):
    prompt = f"""
Hai il compito di generare un bollettino di sicurezza strutturato e professionale. Analizza il testo qui sotto e genera un output nel seguente formato:

---
**Oggetto:**
...

**Ambito:**
...

**Preambolo:**
...

**Stima rischio:**
...

**Tipologia di attacco:**
...

**Prodotti interessati:**
...

**CVE:**
...

**CVSS:**
...

**Riferimenti:**
...

**Descrizione tecnica:**
...

**Note aggiuntive:**
Si consiglia di applicare l'aggiornamento di sicurezza il prima possibile per garantire la protezione contro potenziali sfruttamenti della vulnerabilità.

**Data di pubblicazione:**
[Inserire la data di pubblicazione del bollettino]

**Firma:**
[Nome del responsabile della sicurezza o dell'autore del bollettino]
[Titolo del responsabile]
[Nome dell'organizzazione]

**Contatti:**
Per ulteriori informazioni o assistenza, contattare il team di sicurezza informatica all'indirizzo [email@example.com] o al numero [telefono].
---

Testo documento:
{testo}
"""

    start = time.time()
    response = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": "Sei un esperto di cybersecurity e compliance."},
            {"role": "user", "content": prompt}
        ]
    )
    end = time.time()
    bollettino = response.choices[0].message.content
    durata = (end - start) / 60
    return bollettino, durata

# Interfaccia Streamlit
st.title("📄 Generatore Bollettini Cybersecurity da PDF")

uploaded_file = st.file_uploader("📎 Carica un documento PDF", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF caricato con successo.")

    if st.button("🧠 Genera bollettino"):
        with st.spinner("⏳ Estrazione e generazione in corso..."):
            testo_estratto = estrai_testo_pdf(uploaded_file)
            bollettino, durata = genera_bollettino_da_testo(testo_estratto)

        st.success(f"✅ Bollettino generato in {durata:.2f} minuti.")
        st.subheader("📋 Anteprima del Bollettino")
        st.text_area("Contenuto del bollettino", bollettino, height=500)

        # Salvataggio Word
        doc = Document()
        doc.add_heading("Bollettino di Sicurezza", level=1)
        doc.add_paragraph(bollettino)
        output_path = "Bollettino_Sicurezza.docx"
        doc.save(output_path)

        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 Scarica bollettino Word",
                data=f,
                file_name=output_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
