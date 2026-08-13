# Gate G2 — Alpha rules-locked

**Versione:** 0.9.0-beta.2  
**Data:** 13 agosto 2026  
**Esito attuale:** **PENDING — rules-lock candidate tecnicamente valida, evidenze umane mancanti**  
**Fase:** 2 — Consolidamento delle regole

## Perché G2 non è ancora PASS

Il piano richiede criteri che non possono essere certificati dal solo manoscritto o da test automatici: un Custode nuovo deve formulare due prezzi di Risonanza in meno di 45 secondi; due Custodi indipendenti devono produrre lo stesso ordine sostanziale del round; tester indipendenti devono calcolare Sangue Tenace nello stesso modo. Queste evidenze devono essere raccolte realmente e non vengono simulate.

Il protocollo da usare è `docs/playtest/PHASE2_RULES_TEST_SCRIPT.md`.

## Stato R2.1 — Risonanza

**Sorgenti: COMPLETE. Evidenza umana: PENDING.**

Implementato:

- un solo testo canonico in MR-RULE-015;
- eleggibilità limitata a Usare Potere e Mosse Esclusive di Casata con tiro;
- ordine Fato → risultato finale → eventuale Risonanza;
- sostituzione dell'esito originario senza doppia conseguenza;
- procedura di validità dei prezzi;
- 96 esempi strutturati: 4 Casate × 4 categorie × 6;
- esempi di prezzi vaghi, retroattivi, sproporzionati, categorie finte, costi riciclati e Anima senza via di risoluzione;
- procedura operativa in 45 secondi.

**Issue:** RULE-003 resta `in_progress` fino al test G2-A.

## Stato R2.2 — Anello, rimozione e Rinuncia

**COMPLETE.**

MR-RULE-017 distingue:

1. Anello tolto;
2. separazione temporanea;
3. cessione;
4. Rinuncia.

La morte è separata. Togliere, perdere temporaneamente o cedere l'oggetto non trasferisce il legame, non equivale a Rinuncia e non genera penalità permanenti automatiche. La Rinuncia è volontaria, consensuale e dichiarata come procedura di campagna.

**Issue chiusa:** RULE-001 / P0-04.

## Stato R2.3 — Round di combattimento

**Sorgenti: COMPLETE. Evidenza umana: PENDING.**

MR-RULE-008 introduce una unità di minaccia con un budget ordinario di una Azione Significativa per round. Danno pieno, Condizione, spostamento forzato, presa di obiettivo o Mossa offensiva nominata spendono il budget. Una minaccia già attivata non riceve un secondo attacco pieno tramite un successivo 7–9/6−; il Custode usa pressione, posizione, clock o nuove minacce. I minion combinati condividono un budget.

`docs/rules/COMBAT_ROUND_EXAMPLE.md` contiene quattro Guardiani, due minion combinati e un Dullahan.

**Issue:** RULE-004 resta `in_progress` fino al test G2-B con due Custodi indipendenti.

## Stato R2.4 — Escalation

**COMPLETE.**

MR-RULE-009 applica il bonus al massimo una volta per Azione Principale che infligge danno. Area e multi-colpo scelgono una sola istanza o un solo bersaglio; reazioni, attacchi bonus, danni persistenti e azioni autonome delle evocazioni non moltiplicano il bonus. `docs/rules/ESCALATION_CASES.md` documenta cinque casi limite.

**Issue chiusa:** RULE-005 / P1-03.

## Stato R2.5 — Recupero, Burnout e condizioni

**COMPLETE sul piano normativo.**

MR-RULE-012 fissa i verbi:

- subire Stress;
- recuperare Stress;
- spendere PF;
- subire danno;
- perdere PF soltanto quando una regola lo dichiara.

Il Burnout usa il sovraccarico oltre Stress 10 e non la vecchia formula del costo raddoppiato. La regola generale **Nessun ciclo a guadagno netto** vive nel Capitolo 5; le capacità locali rinviano a quella fonte e mantengono soltanto limiti specifici.

**Issue chiusa:** RULE-007.

## Stato R2.6 — Sangue Tenace

**Sorgenti: COMPLETE. Evidenza umana: PENDING.**

MR-RULE-013 stabilisce:

- una volta per scena;
- controllo dopo il costo finale e prima della spesa;
- trigger soltanto se il pagamento integrale porterebbe **sotto** il 40% dei PF massimi;
- costo minimo 2 PF;
- Stress iniziale 0–8;
- PF convertiti = `floor(costo / 2)`, minimo 1, massimo `costo - 1`;
- spesa dei PF residui + 2 Stress;
- Armatura e resistenze non modificano un costo in PF;
- riduzioni esplicite del costo avvengono prima;
- Corpo della Risonanza non è eleggibile.

Il capitolo Mictlan contiene esempi sui costi 1, 2, 3 e 5 PF e sulla soglia del 40%.

**Issue:** RULE-006 resta `in_progress` fino al test G2-D.

## P0-05 — Velo Tracker

**CHIUSO.** MR-RULE-018 rende il Velo Tracker 0–12 l'unica scala meccanica globale. Il termine *esposizione* può restare descrittivo, ma non esiste un secondo tracker 0–4.

**Issue chiusa:** RULE-002.

## Controllo tecnico

Eseguire:

```bash
npm run phase2:check
```

Il controllo aggrega G0, G1 e `scripts/validate_rules_phase2.py`. Il validator Fase 2 verifica tra l'altro:

- MR-RULE-001..018 presenti;
- 96 prezzi di Risonanza;
- quattro stati dell'Anello;
- budget di Azione Significativa;
- cinque casi Escalation;
- regressioni di terminologia Stress/PF e vecchio Burnout;
- formula ed esempi Sangue Tenace;
- singolo Velo Tracker 0–12;
- glossary e style guide aggiornati;
- assenza di vecchi nomi da pregenerato nei prodotti di onboarding.

## Evidenze ancora necessarie

Per trasformare questo documento in **G2 PASS** devono esistere dati compilati per:

- **G2-A:** due Custodi indipendenti, mediana <45 secondi sui prezzi e ≥5/6 prompt validi al primo tentativo;
- **G2-B:** due Custodi indipendenti con ordine sostanziale concorde e nessuna doppia Azione Significativa;
- **G2-C:** applicazione concorde dei cinque casi Escalation;
- **G2-D:** calcoli Sangue Tenace concordi per costo minimo, 2, 3, 5 PF, soglia 40% e Stress 9;
- **G2-E:** nessuna confusione tra subire/recuperare Stress, spesa PF e danno.

## Issue non appartenente al rules lock ma ancora P0

`PROD-001 — Correggere simboli e tabelle corrotte` resta aperta perché la prova di chiusura richiede QA visivo degli artefatti costruiti. Deve essere chiusa prima di dichiarare la beta blind-ready al Gate G3.

## Decisione

**NO-GO alla dichiarazione G2 PASS.**  
**GO alla raccolta controllata delle evidenze G2** usando il protocollo preparato. Nessuna nuova regola viene aggiunta durante questi test; eventuali difetti replicati riaprono la fonte competente.
