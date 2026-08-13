# Gate G0 — Baseline congelata

**Versione valutata:** 0.9.0-beta.2 Ring Core  
**Data:** 13 agosto 2026  
**Esito:** **PASS**

G0 verifica soltanto la preparazione e il controllo del progetto. Non certifica canon, bilanciamento, blind playtest o qualità commerciale.

## P0.1 — Congelare la baseline

**Esito: PASS**

Evidenze:

- snapshot sorgente immutabile: `archive/baselines/0.9.0-beta.2/source_snapshot.tar.gz`;
- 103 file sorgente nella baseline;
- SHA-256 snapshot: `c057d11942d1753dcac8dc2a98c4ac06da5d439e071ac0138e97b5147921062a`;
- manuale PDF di riferimento: `Mythic_Rings_Prima_Edizione_0.9.0-beta.2_RING_CORE_COMPLETO.pdf`;
- pagine manuale: **265**;
- SHA-256 manuale: `043b4401e5baa0b40f237e14558d1a0643e8d7862c0dee4b173766713e71dc4d`;
- convenzioni ID: `docs/project/ID_CONVENTIONS.md`;
- changelog master strutturato in `canon`, `rules`, `balance`, `text`, `layout`: `docs/project/CHANGELOG_MASTER.csv`;
- verifica automatica: `python3 scripts/verify_baseline.py`.

La baseline non viene sovrascritta: una futura baseline deve usare una nuova directory/versione.

## P0.2 — Registro delle criticità

**Esito: PASS**

Evidenze:

- `docs/project/ISSUE_REGISTER.csv`: **22 issue** importate dal piano;
- P0 aperti: **7**;
- ogni P0 possiede owner, data obiettivo, fonte e criterio di chiusura;
- `docs/project/DECISION_REGISTER.csv`: **8 decisioni** aperte richieste al lead designer entro G1;
- difetti, scelte di design, domande di playtest e preferenze/stile sono campi distinti;
- i riferimenti originali `P0-01`…`P1-08` restano conservati in `roadmap_ref`;
- nessun ID duplicato rilevato all'importazione;
- verifica automatica: `python3 scripts/validate_project_governance.py`.

## P0.3 — Modello dati del playtest

**Esito: PASS**

Evidenze:

- specifica: `docs/playtest/DATA_MODEL.md`;
- schema: `docs/playtest/schema/session_bundle.schema.json`;
- template bundle: `docs/playtest/templates/session_bundle.template.json`;
- moduli separati per sessione, PG, Risonanza, combattimento, consultazioni, issue e post-sessione;
- ID anonimi senza nomi, email, handle o localizzazione precisa;
- fixture sintetica: `tests/fixtures/playtest_phase0_smoke/session_bundle.json`;
- validator: `scripts/validate_playtest_dataset.py`.

Smoke test eseguito con successo:

- 4 personaggi;
- 2 eventi di Risonanza;
- 2 round di combattimento;
- 2 consultazioni di regole;
- 1 issue di esempio;
- mediana sintetica decisione Risonanza: 27 s;
- mediana sintetica consultazione: 37 s.

I valori sono **fixture tecniche**, non risultati di un playtest umano.

## Criterio G0

La baseline è identificabile e immutabile, il backlog è amministrabile e il kit dati può rappresentare una sessione completa. Tutti i criteri della Fase 0 risultano verificabili e superati.

## Rischi ancora aperti

- Il PDF di riferimento non è duplicato nella repository: è identificato da nome, numero di pagine e checksum; la fonte sorgente è invece archiviata internamente.
- Nessun dato della fixture può essere usato per bilanciamento o gradimento.
- I P0 di canon e regole restano deliberatamente aperti: appartengono alle fasi successive.

## Prossimo gate

**G1 — Canon approvato.**  
Il lavoro successivo parte da `CANON-001`, `CANON-002`, `CANON-003`, `CANON-004`, `RULE-002` e dalle decisioni `DEC-001`–`DEC-008`, senza aggiungere nuovi sottosistemi.
