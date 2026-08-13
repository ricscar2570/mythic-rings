# Changelog

## 0.9.0-beta.2 — Ring Core

### Fase 0 — governance e baseline

- congelata una baseline sorgente immutabile della beta.2 con checksum e riferimento univoco al manuale da 265 pagine;
- definite convenzioni ID stabili per regole, poteri, PNG, luoghi, avversari, issue e decisioni;
- introdotto changelog master strutturato nelle categorie canon, rules, balance, text e layout;
- creato il registro unico delle criticità con 22 issue, 7 P0 dotati di owner/data/criterio di chiusura e 8 decisioni aperte verso G1;
- introdotto il modello dati playtest v1 con schema, moduli anonimi, fixture sintetica e validator;
- aggiunti controlli automatici `baseline:check`, `governance:check`, `playtest:data:check` e `phase0:check`;
- chiuso formalmente `G0 — Baseline congelata` con report verificabile.


### Fase 1 — canonizzazione del mondo

- chiuso `G1 — Canon approvato` con cinque Linee Ley, Nexus centrale e cinque Nexus Secondari in fonte strutturata;
- eliminati bonus/malus locali generici da Linee, Nexus e risorse di quartiere;
- unificata la Cerchia: Elisabetta Conti Presidente neutrale, Eleonora Visconti Anziana Avalon/coordinatrice, Leila Ferrara Umbra, Kwame Asante Ife, Marisol Reyes Mictlan;
- separati Padre Tommaso (mentore) e Valentina Riva (mediatrice indipendente) dai ruoli della Cerchia e dai pregenerati;
- introdotta una cronologia canonica di 12 eventi che distingue storia reale, evento misto e fiction;
- rimossa la formulazione storica obsoleta su Milano “devastata” nel 1224 e le migrazioni inventate usate per spiegare Ife/Mictlan;
- corretto l'anacronismo che collegava il Cimitero Monumentale ai protocolli del 1630;
- adottato il presente mobile “Milano, oggi” e normalizzati Comune, Città Metropolitana, Custodi, Società del Velo e numero di Anelli;
- registrate come accepted le otto decisioni G1 e chiusi CANON-001..004;
- aggiunti `docs/CANON_BIBLE.md`, `docs/CANON_ROSTER.md`, `docs/CANON_TIMELINE.md`, `data/canon/*` e `scripts/validate_world_canon.py`;
- aggiunti i comandi `canon:check` e `phase1:check`; `verify` comprende ora anche G1.


### Fase 2 — consolidamento delle regole (rules-lock candidate)

- formalizzati i quattro stati dell’Anello e la Rinuncia consensuale in MR-RULE-017;
- unificato il Velo Tracker globale 0–12 in MR-RULE-018, senza scala Esposizione 0–4 concorrente;
- completata la libreria operativa della Risonanza con 96 prezzi e procedura in 45 secondi;
- definito un budget di Azione Significativa per ogni unità di minaccia e aggiunto l’esempio completo di round;
- definita l’Escalation una sola volta per Azione Principale che infligge danno, con cinque casi limite;
- consolidati verbi delle risorse, Burnout e regola unica anti-ciclo;
- resa procedurale Sangue Tenace con esempi sui costi 1/2/3/5 PF e soglia strettamente sotto il 40%;
- aggiunto `scripts/validate_rules_phase2.py` e il comando `phase2:check`;
- preparato `docs/playtest/PHASE2_RULES_TEST_SCRIPT.md` per le evidenze indipendenti necessarie a G2.

**Stato gate:** la coerenza tecnica della rules-lock candidate è verificata, ma **G2 resta PENDING** finché i criteri umani del piano non sono osservati e registrati.

### Preparazione Fase 3 — playtest interno

- preparata la sequenza completa di 12 sessioni nei sei blocchi A–F previsti dal piano;
- coperta la matrice di bilanciamento B1–B8 con scenari e composizioni esplicite;
- aggiunte soglie decisionali 35% / 30% / 50% / 25% e vincolo di tre osservazioni comparabili;
- aggiunto un analizzatore di bundle reali per Risonanza, consultazioni, combattimento, spotlight, interesse per una seconda sessione e red flag;
- lo stato resta `prepared_not_executed`: nessun risultato umano è stato inventato o sostituito da fixture.

- introdotta **Risonanza dell'Anello** (MR-RULE-015), meccanica-identità 1/scena che migliora 6−→7–9 o 7–9→10+ pagando un prezzo dichiarato;
- introdotte le quattro categorie di prezzo **Corpo, Anima, Legame, Mondo** senza aggiungere nuovi tracker;
- introdotta **Ancora dell'Anello** (MR-RULE-016), collegata a un Legame L1+ e utilizzabile una volta per sessione;
- rinominata la capacità L3 del Legame Amato da Ancora a **Radicamento** per eliminare collisioni terminologiche;
- aggiunte procedure per Custode, FAQ, quick reference, quickstart, kit e avventura di playtest;
- aggiunte metriche dedicate per misurare dominanza dei prezzi, frequenza d'uso, rifiuti e impatto sulla fascia 7–9;
- chiarita la lore: le quattro sono **stirpi di Anelli**, non quattro soli artefatti; a Milano sono attivi circa quaranta Anelli, in rapporto ai Guardiani operativi;
- resa la versione dei prodotti derivata dal manifest invece che hardcoded nei principali script di build.
- definita in modo chiuso l'eleggibilità della Risonanza: solo **Usare Potere** e **Mosse Esclusive di Casata con tiro**;
- formalizzata la validità dei quattro prezzi, incluso il limite di Mondo a Velo 12 e il divieto di prezzi fittizi o già pagati;
- aggiunto il modello matematico e le red flag di playtest in `docs/RING_CORE_BALANCE_MODEL.md`;
- riallineate le fasce di distanza di quickstart e kit e rimossi bonus ad hoc per gruppi piccoli incompatibili con i limiti canonici;
- chiarita la separazione fisica dall'Anello e aggiunti esempi completi di Condizione con limite e via di risoluzione.
- chiuso il confine di scena della Risonanza: round, pause brevi e spostamenti tattici non resettano l'uso;
- normato il rifiuto dei prezzi: dopo due prezzi validi dichiarati l'opportunità 1/scena è spesa; se non esistono due prezzi validi la procedura non parte;
- reso **Mondo** dipendente sempre dal Velo Tracker, eliminando il fallback senza tracker;
- riallineata la style guide editoriale e protette terminologia, distanze e ruolo del Custode con test di regressione;
- aggiunto `docs/QA_REPORT_0.9.0-beta.2.md` con stato verificato e gate ancora aperti.

## Correzione pipeline CI della 0.9.0-beta.1

- reso `release:check` autosufficiente su checkout puliti: ricostruisce `dist/` prima del preflight;
- introdotto `release:preflight` per il controllo rapido degli artefatti già costruiti;
- mantenuto `release:build` come alias esplicito del gate completo;
- riallineati workflow CI, README e guida alla contribuzione alla nuova semantica dei comandi.
- resa deterministica la conversione LibreOffice dei prodotti: un PDF completo e stabile viene validato e il processo headless eventualmente rimasto sospeso viene terminato in modo controllato.
- aggiornato il lockfile npm: `npm audit` non segnala vulnerabilità note nella dipendenza risolta.
- verificato `npm run release:check` da `dist/` assente: exit code 0, 13 artefatti validi.

## 0.9.0-beta.1

- introdotta una fonte canonica delle regole;
- unificati Punti Fato, Legami, Riprendersi e Ultimo Respiro;
- normalizzati danno, Armatura e combattimento player-facing;
- Escalation spostata dal tiro al danno;
- Investigare riscritto in forma fail-forward;
- rimossi riferimenti interni alle patch dal manuale;
- aggiunti manifest, gate di release, style guide e protocollo di playtest;
- aggiornata la pipeline per produrre artefatti con metadati unici;
- rimossi placeholder noti da colophon e crediti.
- sviluppata la campagna *Il Crepuscolo del Velo* con procedure di conduzione, stato persistente e finali reattivi;
- ampliato il quickstart con Condizioni, equipaggiamento, esempio di tiro, preparazione del Custode e checklist blind;
- ricostruito il Kit del Giocatore con scheda, tracker, mosse, Legami, avanzamento e sicurezza;
- aggiunta *Notte al Monumentale* come avventura autonoma con handout e rapporto di playtest;
- aggiornati audit e preflight per includere tutti i prodotti di ingresso;
- riscritto il README per riflettere la pipeline e la struttura effettive;
- completata l'ispezione visiva integrale di manuale, quickstart, kit e avventura;
- reso atomico e incrementale il post-processing PDF, con verifica prima della sostituzione;
- isolate le conversioni LibreOffice con profili temporanei, timeout e terminazione controllata;
- ridotti i segnalibri dei prodotti ai soli livelli editorialmente utili;
- superato il preflight tecnico dei quattro PDF;
- documentato l'audit DOCX e il limite noto relativo alle tabelle di impaginazione;
- aggiunto il rapporto di qualità `docs/QA_REPORT_0.9.0-beta.1.md`;
- introdotto un lock di paginazione verificato, con build PDF ordinaria a un passaggio e comando separato di rigenerazione;
- separati il controllo rapido `release:preflight` e il gate autosufficiente `release:check`/`release:build`, che ricostruisce l’intera distribuzione.

## Archivio 3.2

Il changelog storico della revisione 3.2 è conservato in `archive/CHANGELOG_v3.2_fix.md`.
