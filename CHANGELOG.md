# Changelog

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
