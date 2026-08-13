# Mythic Rings — Protocollo di verifica G2

**Versione:** 0.9.0-beta.2  
**Scopo:** raccogliere le evidenze umane richieste dal piano per chiudere il Gate G2.  
**Regola:** il facilitatore non spiega la regola prima del compito. Registra prima l'interpretazione spontanea; chiarimenti e debriefing vengono dopo.

## Campione minimo per il Gate G2

- **2 Custodi indipendenti** che non abbiano partecipato alla scrittura, per Risonanza e round.
- **3 tester indipendenti** per i calcoli di Sangue Tenace.
- Almeno **1 tester** non abituato a Mythic Rings tra i due Custodi, così da misurare la reperibilità del testo.

Questi numeri servono soltanto al rules lock G2. Il campione esteso del blind playtest G4 resta quello definito dal piano di sviluppo.

## Test G2-A — Risonanza in meno di 45 secondi

Per ogni Custode eseguire **6 prompt** senza consultare la libreria di esempi, consentendo soltanto manuale/quick reference.

Per ogni prompt registrare:

1. tempo dal termine della lettura della situazione alla dichiarazione completa dei due prezzi;
2. categorie scelte;
3. formulazione esatta;
4. se entrambi i prezzi sono immediati, concreti, differenti e realmente applicabili;
5. se il prezzo sostituisce correttamente la conseguenza originaria;
6. eventuale pagina o sezione consultata.

### Prompt

1. Avalon, Usare Potere, risultato 6−, ostaggio in pericolo, Velo 4.
2. Umbra, Mossa Esclusiva con tiro, risultato 7–9, un Legame L2 è raggiungibile, Velo 11.
3. Ife, Usare Potere di guarigione, risultato 6−, Guardiano a 5 PF, Velo 12.
4. Mictlan, Usare Potere, risultato 7–9 dopo avere già speso PF, Velo 7.
5. Avalon, risultato 7–9, nessun Legame raggiungibile nella fiction.
6. Umbra, risultato 6−, il giocatore ha già una Condizione dell'Anello affine a quella che verrebbe proposta.

### Criterio di chiusura

Per **entrambi** i Custodi:

- mediana dei sei tempi <45 secondi;
- nessun prezzo nascosto o retroattivo;
- almeno 5/6 prompt con due prezzi validi al primo tentativo;
- nessuna doppia conseguenza dopo una Risonanza accettata.

## Test G2-B — Round e Azioni Significative

Dare ai due Custodi `docs/rules/COMBAT_ROUND_EXAMPLE.md`, poi consegnare la situazione senza soluzione:

- quattro Guardiani: Marco, Chiara, Luca, Elena;
- un Dullahan;
- due Segugi d'Ombra combinati come gruppo di minion;
- round 3;
- un 7–9 contro il Dullahan dopo che il Dullahan ha già inflitto il proprio danno pieno nello stesso round;
- Segugi ancora liberi a fine round.

Chiedere a ciascun Custode di scrivere, in ordine:

1. quali unità possiedono un budget;
2. quale evento lo spende;
3. che cosa può fare il Dullahan sul secondo 7–9;
4. chi agisce a fine round;
5. quando si ripristinano i budget.

### Criterio di chiusura

- i due Custodi producono lo stesso ordine sostanziale di risoluzione;
- nessuna unità ottiene due Azioni Significative per errore;
- il secondo 7–9 contro una minaccia già attivata genera pressione/posizione/clock/nuova minaccia, non un secondo danno pieno della stessa unità.

## Test G2-C — Escalation, cinque casi

Senza mostrare la soluzione, chiedere di applicare l'Escalation al round 4 (+2):

1. un singolo attacco a un bersaglio;
2. un'area che danneggia tre bersagli;
3. una Azione Principale con tre colpi;
4. un effetto persistente che torna a fare danno nel round successivo;
5. un'evocazione che agisce autonomamente e una evocazione comandata spendendo l'Azione Principale.

Confrontare con `docs/rules/ESCALATION_CASES.md` **solo dopo** le risposte.

### Criterio di chiusura

Tutti i tester applicano il bonus al massimo una volta per Azione Principale e non lo moltiplicano per colpi o bersagli.

## Test G2-D — Sangue Tenace

Assumere che la soglia sotto il 40% sia soddisfatta, salvo quando indicato.

| Caso | Costo finale | Risposta canonica |
|---|---:|---|
| Minimo | 1 PF | Sangue Tenace non si attiva |
| A | 2 PF | spendi 1 PF, subisci 2 Stress |
| B | 3 PF | spendi 2 PF, subisci 2 Stress |
| C | 5 PF | spendi 3 PF, subisci 2 Stress |
| Soglia | il pagamento lascia esattamente al 40% | non si attiva |

Ripetere A–C con Stress iniziale 9: Sangue Tenace non è eleggibile perché il Guardiano non può subire interamente 2 Stress.

### Criterio di chiusura

Tutti i tester producono gli stessi valori senza spiegazione del designer.

## Test G2-E — Burnout e verbi delle risorse

Chiedere di risolvere questi casi:

1. Stress 9, costo base 2 Stress: il costo finale diventa 3; 1 porta a 10, 2 sono sovraccarico → perdita 4 PF e Sfidare il Pericolo +FAT.
2. Stress 10, effetto «porta lo Stress a 10»: conta come 1 punto di sovraccarico → perdita 2 PF e procedura Burnout.
3. Un effetto dice «subisci 2 Stress»: il tracker aumenta di 2, non diminuisce.
4. Un effetto dice «recuperi 2 Stress»: il tracker diminuisce di 2, non aumenta.
5. Una spesa in PF non viene ridotta dall'Armatura.

### Criterio di chiusura

Nessun tester confonde subire/recuperare Stress o spesa/danno PF; i primi due casi producono la stessa sequenza.

## Registrazione

Usare:

- `docs/playtest/forms/RULE_LOOKUP_LOG.csv` per tempi e ricerche;
- `docs/playtest/forms/ISSUE_LOG.csv` per divergenze;
- `docs/playtest/forms/RESONANCE_LOG.csv` per G2-A;
- `docs/playtest/forms/COMBAT_LOG.csv` per G2-B/C.

Al termine, il Rules editor crea `docs/gates/G2_EVIDENCE.md` con risultati grezzi, deviazioni, issue aperte e decisione **PASS / NO-GO**. Non si chiude G2 sulla base di simulazioni o autovalutazione del designer.
