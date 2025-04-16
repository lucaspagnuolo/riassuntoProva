import streamlit as st
import requests
from bs4 import BeautifulSoup
from mistralai import Mistral
import time
from docx import Document  # <-- nuova libreria, più semplice di Spire

# Carica chiave API
try:
    api_key = st.secrets["MISTRAL_API_KEY"]
except KeyError:
    st.error("❌ Chiave API non trovata nei secrets. Inseriscila nei settings di Streamlit.")
    st.stop()

model = "mistral-large-latest"
client = Mistral(api_key=api_key)

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
        h1 = soup.find("h1", class_="ms-fontWeight-semibold")
        if not h1:
            st.error("❌ Impossibile trovare il nome del prodotto.")
            st.stop()
        nome_prodotto = h1.get_text(strip=True).replace("New", "").strip()

        # Versione fissa
        prima_li = soup.find("li")
        if not prima_li:
            st.error("❌ Versione fissa non trovata.")
            st.stop()
        versione_fissa = prima_li.text.strip()

        # Tipo vulnerabilità
        impact_dt = soup.find("dt", string="Impact")
        if not impact_dt:
            st.error("❌ Tipologia di vulnerabilità non trovata.")
            st.stop()
        tipo_vulnerabilita = impact_dt.find_next_sibling("dd").text.strip()

        # CVSS Score
        cvss_dd = soup.find("dd", string=lambda s: s and "CVSS:3.1" in s)
        if not cvss_dd:
            st.error("❌ CVSS non trovato.")
            st.stop()
        cvss_score = cvss_dd.text.split()[1]
        rischio = calcola_rischio(cvss_score)

        # Descrizione tecnica
        descrizione_div = soup.find("div", class_="css-342")
        if not descrizione_div:
            st.error("❌ Descrizione tecnica non trovata.")
            st.stop()
        descrizione = descrizione_div.get_text(strip=True)

        cve_id = cve_url.split("/")[-1]

        # Prompt da passare a Mistral
        prompt = f"""
Costruisci un bollettino cybersecurity nel seguente formato:

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

        # Chiamata a Mistral
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
        st.error(f"❌ Errore durante l'elaborazione: {e}")
        st.stop()

# Interfaccia Streamlit
st.title("🛡️ Generatore automatico di bollettini Cybersecurity (CVE Microsoft)")

url_input = st.text_input("🔗 Inserisci l'URL della vulnerabilità Microsoft (CVE)")

if url_input:
    if st.button("🧠 Genera bollettino"):
        with st.spinner("🔍 Estrazione e analisi in corso..."):
            bollettino, durata = genera_bollettino(url_input)

        st.success(f"✅ Bollettino generato in {durata:.2f} minuti")

        st.subheader("📄 Anteprima Bollettino")
        st.text_area("Contenuto", bollettino, height=400)

        # Salvataggio Word con python-docx
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
