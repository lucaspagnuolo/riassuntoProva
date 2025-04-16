import streamlit as st
import requests
from bs4 import BeautifulSoup
from mistralai import Mistral
import time
from docx import Document

# Recupera API key
try:
    api_key = st.secrets["MISTRAL_API_KEY"]
except KeyError:
    st.error("❌ Chiave API non trovata nei secrets.")
    st.stop()

client = Mistral(api_key=api_key)
model = "mistral-large-latest"

def calcola_rischio(cvss_score):
    try:
        score = float(cvss_score)
        if score >= 9.0:
            return "Critica"
        elif score >= 7.0:
            return "Alta"
        elif score >= 4.0:
            return "Media"
        else:
            return "Bassa"
    except:
        return "Non determinabile"

def genera_bollettino(cve_url):
    response = requests.get(cve_url)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        # Nome prodotto
        nome_prodotto = "Non trovato"
        h1_tags = soup.find_all("h1")
        for h1 in h1_tags:
            text = h1.get_text(strip=True)
            if "Vulnerability" in text:
                nome_prodotto = text.replace("New", "").strip()
                break

        # Versione fissa
        versione_fissa = "Non specificata"
        li_tag = soup.find("li")
        if li_tag:
            versione_fissa = li_tag.get_text(strip=True)

        # Tipologia di vulnerabilità
        tipo_vulnerabilita = "Non disponibile"
        impact_dt = soup.find("dt", string=lambda s: s and "Impact" in s)
        if impact_dt:
            tipo_vulnerabilita = impact_dt.find_next_sibling("dd").get_text(strip=True)

        # CVSS
        cvss_score = "N/A"
        cvss_text = soup.find("dd", string=lambda s: s and "CVSS:3.1" in s)
        if cvss_text:
            try:
                cvss_score = cvss_text.get_text(strip=True).split()[1]
            except IndexError:
                pass
        rischio = calcola_rischio(cvss_score)

        # Descrizione tecnica
        descrizione = "Nessuna descrizione disponibile."
        p_tag = soup.find("p")
        if p_tag:
            descrizione = p_tag.get_text(strip=True)

        # CVE ID
        cve_id = cve_url.split("/")[-1]

        # Prompt per Mistral
        prompt = f"""
Oggetto
Nuova vulnerabilità risolta in {nome_prodotto.split()[0]}

Ambito
PDL, Software, Microsoft, Edge

Preambolo
Si segnala la pubblicazione, da parte di Microsoft, di un aggiornamento di sicurezza volto a correggere la vulnerabilità {cve_id} nel browser {nome_prodotto.split()[0]}.

Stima rischio
{rischio}
(stima Microsoft)

Tipologia di attacco
{tipo_vulnerabilita}

Prodotti interessati
{nome_prodotto}:
- versioni precedenti alla {versione_fissa}

CVE
{cve_id}

CVSS
{cvss_score}

Riferimenti
{cve_url}

Descrizione tecnica
{descrizione}
"""

        start = time.time()
        response = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": "Genera un bollettino professionale nel formato richiesto."},
                {"role": "user", "content": prompt}
            ]
        )
        end = time.time()

        bollettino = response.choices[0].message.content
        durata = (end - start) / 60
        return bollettino, durata

    except Exception as e:
        st.error(f"❌ Errore durante l'analisi della pagina: {e}")
        st.stop()

# Interfaccia Streamlit
st.title("🛡️ Generatore bollettini Cybersecurity (CVE Microsoft)")

url_input = st.text_input("🔗 Inserisci l'URL Microsoft della vulnerabilità")

if url_input:
    if st.button("🧠 Genera bollettino"):
        with st.spinner("⏳ Analisi in corso..."):
            bollettino, durata = genera_bollettino(url_input)

        st.success(f"✅ Bollettino generato in {durata:.2f} minuti")
        st.subheader("📄 Bollettino")
        st.text_area("Contenuto", bollettino, height=400)

        # Salva come Word
        doc = Document()
        doc.add_paragraph(bollettino)
        output_file = "Bollettino_Cybersecurity.docx"
        doc.save(output_file)

        with open(output_file, "rb") as f:
            st.download_button(
                label="📥 Scarica bollettino Word",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
