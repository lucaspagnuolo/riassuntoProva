def genera_bollettino_da_testo(testo):
    if not testo or len(testo.strip()) < 30:
        return "❌ Testo insufficiente o mancante nel PDF.", 0

    prompt = f"""
Agisci come un analista di sicurezza informatica. Riceverai il testo estratto da un documento (es. PDF) che contiene informazioni su una vulnerabilità di sicurezza, come un CVE.

Il tuo compito è creare un bollettino di sicurezza nel seguente formato:

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

Ecco il testo del documento da analizzare:

\"\"\"
{testo}
\"\"\"
"""

    start = time.time()
    response = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": "Sei un esperto in cybersecurity e incident response."},
            {"role": "user", "content": prompt}
        ]
    )
    end = time.time()
    bollettino = response.choices[0].message.content
    durata = (end - start) / 60
    return bollettino, durata
