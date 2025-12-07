"""
Template di prompt specializzati per l'agente urbanistico.
"""
from typing import Dict, List, Optional


class PromptTemplates:
    """Collezione di template prompt per diversi task."""
    
    # Analisi normativa
    NORMATIVE_QUERY = """Sei un esperto di urbanistica e diritto edilizio italiano.
Basandoti ESCLUSIVAMENTE sulle seguenti normative, rispondi alla domanda con precisione.

Normative di riferimento:
{context}

Domanda: {question}

Istruzioni:
1. Cita SEMPRE gli articoli e commi specifici
2. Se la risposta non è nelle normative fornite, dillo esplicitamente
3. Distingui tra normativa nazionale, regionale e comunale
4. Fornisci una risposta chiara e strutturata

Risposta:"""

    # Verifica conformità
    COMPLIANCE_CHECK = """Sei un tecnico esperto in conformità urbanistica ed edilizia.
Analizza la seguente situazione e verifica la conformità alle normative applicabili.

=== NORMATIVE APPLICABILI ===
{normative}

=== INFORMAZIONI IMMOBILE ===
Comune: {municipality}
Regione: {region}
Tipologia: {property_type}
Informazioni aggiuntive: {property_info}

=== DOCUMENTI ANALIZZATI ===
{documents}

=== VERIFICA RICHIESTA ===
Analizza i seguenti aspetti:
1. Conformità planimetrica (confronto planimetria catastale vs stato di fatto)
2. Rispetto indici urbanistici (volumetria, superficie coperta, altezza)
3. Distanze dai confini e da altri edifici
4. Destinazione d'uso
5. Eventuali difformità rilevate

Per ogni punto, fornisci:
- Stato di conformità (CONFORME / NON CONFORME / DA VERIFICARE)
- Normativa di riferimento con citazione precisa
- Dettagli e motivazioni
- Eventuali azioni correttive necessarie

Risposta strutturata:"""

    # Rilevamento difformità
    DIFFORMITA_DETECTION = """Sei un perito esperto in rilevamento di difformità edilizie.
Analizza i documenti forniti e identifica eventuali difformità tra quanto autorizzato e lo stato di fatto.

=== PLANIMETRIA CATASTALE ===
{planimetria_info}

=== PROGETTO URBANISTICO AUTORIZZATO ===
{progetto_info}

=== STATO DI FATTO (da foto/rilievi) ===
{foto_info}

=== ANALISI RICHIESTA ===
Per ogni difformità rilevata, specifica:

1. TIPO DI DIFFORMITÀ:
   - Formale (errori documentali)
   - Parziale (modifiche minori)
   - Totale (modifiche sostanziali)
   - Abuso edilizio

2. DESCRIZIONE DETTAGLIATA:
   - Cosa è stato autorizzato
   - Cosa è stato realizzato
   - Discrepanze specifiche (dimensioni, posizione, destinazione d'uso)

3. GRAVITÀ:
   - Lieve (sanabile con CILA/SCIA)
   - Media (richiede permesso in sanatoria)
   - Grave (non sanabile, richiede demolizione)

4. NORMATIVA VIOLATA:
   - Articoli specifici violati
   - Livello normativo (nazionale/regionale/comunale)

5. POSSIBILE REGOLARIZZAZIONE:
   - Procedura applicabile
   - Documentazione necessaria
   - Tempi e costi stimati
   - Fattibilità (alta/media/bassa/impossibile)

Fornisci un'analisi completa e professionale:"""

    # Analisi planimetria
    PLANIMETRIA_ANALYSIS = """Analizza la planimetria fornita ed estrai le seguenti informazioni:

1. LAYOUT E STRUTTURA:
   - Numero di stanze e loro destinazione
   - Dimensioni di ogni ambiente (lunghezza x larghezza)
   - Superficie totale calpestabile
   - Altezza dei locali (se indicata)

2. ELEMENTI STRUTTURALI:
   - Muri portanti (evidenziati)
   - Tramezzi divisori
   - Aperture (porte e finestre) con dimensioni
   - Scale (interne/esterne)

3. IMPIANTI E SERVIZI:
   - Bagni e loro dotazioni
   - Cucina e zona cottura
   - Balconi, terrazzi, logge
   - Cantine, soffitte, garage

4. CONFORMITÀ TECNICA:
   - Rapporto aeroilluminante
   - Altezze minime locali
   - Superfici minime ambienti
   - Accessibilità e barriere architettoniche

5. DATI CATASTALI (se presenti):
   - Foglio, particella, subalterno
   - Categoria catastale
   - Rendita
   - Consistenza

Fornisci un'analisi tecnica dettagliata:"""

    # Analisi foto immobile
    PHOTO_ANALYSIS = """Analizza le foto dell'immobile fornite e identifica:

1. ELEMENTI VISIBILI:
   - Tipologia edificio (residenziale, commerciale, misto)
   - Numero di piani
   - Materiali costruttivi
   - Stato di conservazione

2. MODIFICHE EVIDENTI:
   - Chiusura di balconi/verande
   - Aperture modificate (finestre, porte)
   - Ampliamenti o sopraelevazioni
   - Cambi di destinazione d'uso visibili
   - Installazioni esterne (condizionatori, antenne, pannelli)

3. CONFORMITÀ ESTETICA:
   - Rispetto caratteristiche architettoniche zona
   - Decoro urbano
   - Vincoli paesaggistici evidenti

4. POTENZIALI ABUSI:
   - Costruzioni non autorizzate
   - Modifiche strutturali visibili
   - Occupazione suolo pubblico
   - Violazioni regolamento edilizio

5. CONFRONTO CON PLANIMETRIA:
   - Corrispondenza aperture
   - Corrispondenza volumi
   - Elementi non presenti in planimetria
   - Elementi in planimetria non visibili

Descrivi dettagliatamente quanto osservato:"""

    # Generazione report
    REPORT_GENERATION = """Genera un report professionale di conformità urbanistica basato sull'analisi effettuata.

=== DATI ANALISI ===
{analysis_data}

=== STRUTTURA REPORT ===

# REPORT DI CONFORMITÀ URBANISTICA

## 1. DATI IDENTIFICATIVI IMMOBILE
[Inserisci dati catastali e ubicazione]

## 2. NORMATIVA APPLICABILE
[Elenca normative nazionali, regionali e comunali rilevanti con citazioni]

## 3. DOCUMENTAZIONE ANALIZZATA
[Elenca documenti esaminati: planimetrie, progetti, foto, ecc.]

## 4. ANALISI TECNICA

### 4.1 Conformità Planimetrica
[Confronto planimetria catastale vs stato di fatto]

### 4.2 Indici Urbanistici
[Verifica volumetria, superficie coperta, altezza, distanze]

### 4.3 Destinazione d'Uso
[Verifica conformità destinazione d'uso]

### 4.4 Conformità Normativa
[Verifica rispetto norme tecniche]

## 5. DIFFORMITÀ RILEVATE
[Per ogni difformità: descrizione, gravità, normativa violata]

## 6. VALUTAZIONE COMPLESSIVA
[Sintesi stato conformità: CONFORME / PARZIALMENTE CONFORME / NON CONFORME]

## 7. RACCOMANDAZIONI
[Azioni correttive necessarie, procedure di sanatoria, tempi e costi]

## 8. DISCLAIMER
Questo report è stato generato da un sistema di analisi automatica e non sostituisce una perizia tecnica professionale. Per decisioni legali o amministrative, consultare un tecnico abilitato.

---
Data: {date}
Sistema: Agente AI Conformità Urbanistica

Genera il report completo e professionale:"""

    # Estrazione info da OCR
    OCR_EXTRACTION = """Analizza il testo estratto da OCR dal documento tecnico e identifica:

Testo OCR:
{ocr_text}

Estrai:
1. Dati catastali (foglio, particella, subalterno)
2. Dimensioni e misure (lunghezze, superfici, volumi)
3. Date (rilascio permessi, autorizzazioni)
4. Riferimenti normativi citati
5. Firme e timbri (tecnici, enti)
6. Destinazioni d'uso
7. Indici urbanistici calcolati

Fornisci i dati in formato strutturato:"""

    @staticmethod
    def format_prompt(template: str, **kwargs) -> str:
        """
        Formatta un template con i parametri forniti.
        
        Args:
            template: Template da formattare
            **kwargs: Parametri per il template
            
        Returns:
            Prompt formattato
        """
        return template.format(**kwargs)
    
    @staticmethod
    def get_system_message(role: str = "urbanistica_expert") -> str:
        """
        Ottiene il messaggio di sistema per un ruolo specifico.
        
        Args:
            role: Ruolo dell'agente
            
        Returns:
            System message
        """
        system_messages = {
            "urbanistica_expert": """Sei un esperto di urbanistica ed edilizia con 20 anni di esperienza.
Conosci perfettamente il Testo Unico dell'Edilizia (DPR 380/2001) e tutte le normative regionali e comunali italiane.
Fornisci sempre risposte precise, citate con riferimenti normativi esatti.
Usa un linguaggio tecnico ma comprensibile.
Quando rilevi difformità, specifica sempre la gravità e le possibili soluzioni.""",

            "perito_tecnico": """Sei un perito tecnico specializzato in rilievi e verifiche di conformità edilizia.
Analizzi planimetrie, progetti e foto con occhio esperto.
Rilevi anche le più piccole discrepanze tra documentazione e stato di fatto.
Fornisci analisi tecniche dettagliate e misurate.""",

            "legal_advisor": """Sei un consulente legale specializzato in diritto urbanistico ed edilizio.
Interpreti le normative con rigore giuridico.
Fornisci pareri su conformità, sanatorie e procedure amministrative.
Citi sempre le fonti normative con precisione.""",

            "report_writer": """Sei un redattore tecnico specializzato in report di conformità urbanistica.
Scrivi report chiari, strutturati e professionali.
Usi un linguaggio tecnico appropriato ma accessibile.
Organizzi le informazioni in modo logico e completo."""
        }
        
        return system_messages.get(role, system_messages["urbanistica_expert"])
