# Stato del prodotto

Versione: **0.9.0-beta.2**  
Ramo di lavoro: **develop/1.0**  
Obiettivo successivo: **Fase 2 — consolidamento delle regole e Gate G2**



## Fase 1 del piano Ring Core — completata

Il **Gate G1 — canon approvato** è chiuso con esito PASS (`docs/gates/G1_CANON_APPROVED.md`). Sono ora vincolanti:

- presente mobile **“Milano, oggi”** e scale demografiche distinte Comune/Città Metropolitana;
- cinque Linee Ley e sei Nexus con percorsi unici e nessun bonus numerico locale generico;
- roster canonico di Cerchia e PNG ricorrenti;
- cronologia di 12 eventi che distingue eventi reali, misti e fittizi;
- quattro stirpi di Anelli precedenti alle Casate moderne;
- numeri organizzativi coerenti per Custodi e Società del Velo;
- otto decisioni G1 registrate e accettate;
- validator `canon:check` e gate aggregato `phase1:check`.

La lettura culturale specialistica di Ife/Mictlan resta esplicitamente aperta come P2 e non viene sostituita dalla canonizzazione interna.

## Fase 0 del piano Ring Core — completata

Il **Gate G0 — baseline congelata** è chiuso con esito PASS (`docs/gates/G0_BASELINE_FROZEN.md`). Sono ora disponibili:

- baseline sorgente immutabile della 0.9.0-beta.2 e identificazione checksum/pagine del manuale di riferimento;
- convenzioni ID stabili per regole, poteri, PNG, luoghi, avversari, issue e decisioni;
- changelog master nelle categorie canon/rules/balance/text/layout;
- registro unico con 22 issue (7 P0) e 8 decisioni aperte;
- modello dati playtest v1, moduli, schema e validator;
- fixture sintetica completa che supera il controllo automatico.

Il prossimo lavoro non aggiunge contenuti: risolve canon, cronologia, geografia occulta, PNG ricorrenti, numeri e istituzioni prima di G1.

## Completato nella presente revisione

### Governance e produzione

- manifest centrale `book.yml`;
- versione e frontmatter sincronizzati;
- ramo di sviluppo e archivio della linea 3.2;
- changelog editoriale pulito;
- CI, issue template e regole di contribuzione;
- build DOCX, HTML e PDF riproducibile;
- conversioni isolate con timeout e terminazione controllata;
- post-processing PDF atomico con verifica di integrità;
- metadati e segnalibri editoriali;
- preflight di tutti i prodotti;
- controllo dei placeholder e della parità tra formati;
- rapporto storico beta.1 in `docs/QA_REPORT_0.9.0-beta.1.md` e audit corrente Ring Core in `docs/QA_REPORT_0.9.0-beta.2.md`.
- `release:check` ricostruisce `dist/` da zero e rigenera il lock di paginazione per la beta; va riconfermato sul runner GitHub pulito. Per RC/1.0 il lock dovrà essere committato e verificato con `release:locked`;
- lockfile npm ripulito da URL di registry specifici dell’ambiente; la verifica vulnerabilità va ripetuta sul runner esterno insieme al gate CI.

### Sistema

- specifica canonica delle regole fondamentali;
- Punti Fato, modificatori, Legami, Riprendersi e Ultimo Respiro unificati;
- danno, Armatura, iniziativa ed Escalation normalizzati;
- indagine fail-forward;
- combattimento interamente player-facing;
- poteri ricondotti ai limiti del sistema;
- bestiario generato da dati strutturati e privo della colonna Attacco;
- FAQ e riferimenti rapidi riallineati.

### Conduzione e contenuti giocabili

- principi e mosse del Custode trasformati in procedure;
- downtime e Reputazione revisionati;
- tre one-shot rese conducibili con verità, indizi, countdown e finali;
- campagna *Il Crepuscolo del Velo* sviluppata in otto sessioni con registro, cast, deviazioni, alleanze, matrici del finale ed epiloghi;
- quickstart autonomo con regole, pregenerati, avventura e strumenti di feedback;
- Kit del Giocatore completo di scheda, tracker, mosse, Legami, avanzamento e sicurezza;
- *Notte al Monumentale* prodotta anche come avventura introduttiva separata con handout e rapporto di sessione.

### Controlli interni disponibili

I controlli visivi e di preflight completi delle **430 pagine della beta.1** restano documentati in `docs/QA_REPORT_0.9.0-beta.1.md` come baseline storica. La beta.2 modifica testo e paginazione e deve quindi generare nuovi artefatti prima che quei risultati possano essere estesi alla nuova versione.

Per la beta.2 sono già stati superati:

- audit semantico di 33 capitoli, 61 poteri e 31 avversari;
- controllo di portabilità della repository;
- validazione YAML e frontmatter della versione 0.9.0-beta.2;
- controllo strutturale delle tabelle e dei box Markdown;
- test di regressione aggiunti per Ring Core, distanze, scaling dei gruppi piccoli e terminologia.

Restano da riconfermare sugli artefatti beta.2: build completa, lock di paginazione, preflight PDF/DOCX e ispezione visiva delle pagine modificate.

## Rifiniture interne non bloccanti

- valutare in futuro la suddivisione o l'alleggerimento del capitolo sui dodici quartieri;
- rifinire gli spazi bianchi prodotti da box indivisibili e chiusure di capitolo durante la fase grafica;
- sostituire i crediti generici dei playtester con nomi autorizzati dopo il blind playtest.

## Non certificabile senza attività esterne

- esito del blind playtest umano;
- developmental e technical editing indipendenti;
- copyediting e correzione bozze indipendenti;
- consulenza legale e fiscale;
- verifica del marchio;
- consulenza culturale;
- crediti nominativi dei playtester;
- prova di mercato, prezzo e conversione;
- successo commerciale.

La versione resta beta finché i gate esterni non sono documentati. Nessuna modifica grafica definitiva è necessaria per eseguire questi test.


## Novità beta.2 — Ring Core

La beta.2 introduce come meccanica-identità la **Risonanza dell'Anello** (MR-RULE-015) e l'**Ancora dell'Anello** (MR-RULE-016). La Risonanza migliora di una fascia un tiro di **Usare Potere** o di una **Mossa Esclusiva di Casata** eleggibile, una volta per scena, in cambio di un prezzo dichiarato tra Corpo, Anima, Legame e Mondo. L'Ancora collega questa scelta a un Legame L1+ senza introdurre un nuovo punteggio.

Queste due regole sono **sperimentali di beta**: non possono essere promosse alla 1.0 senza blind playtest dedicato e dati sulle categorie di prezzo, sui rifiuti e sulla frequenza dei 7–9.
