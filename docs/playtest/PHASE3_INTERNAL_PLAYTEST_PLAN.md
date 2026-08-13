# Mythic Rings — Fase 3: playtest interno

**Versione:** 0.9.0-beta.2  
**Stato:** **PREPARATO, NON ESEGUITO**  
**Fonte operativa:** `data/playtest/phase3_internal_plan.yml`

Questo piano traduce le dodici sessioni previste dalla roadmap in una sequenza eseguibile. Non contiene risultati e non può essere usato come evidenza di playtest finché sessioni reali non sono state svolte e registrate.

## Disciplina

Per ogni sessione:

1. registrare versione, gruppo, composizione, avanzamento e scenario **prima** di giocare;
2. durante la sessione annotare tiri rilevanti, Risonanze, prezzi, risorse, consultazioni e dubbi senza interrompere il ritmo più del necessario;
3. al termine, effettuare un'intervista a caldo di circa 10 minuti distinguendo comprensione, preferenza e risultato fictionale;
4. entro 24 ore il Custode compila il bundle e classifica le issue;
5. ogni due sessioni si effettua triage: si correggono soltanto P0/P1 replicati o problemi con un criterio di progetto esplicito;
6. a fine blocco A–F si congela la sottoversione usata per poter confrontare i dati.

**Non spiegare una regola che il testo dovrebbe rendere comprensibile.** Registra dove il tester l'ha cercata e quale interpretazione ha scelto.

## Blocco A — Sessioni 1–2

**Focus:** onboarding, creazione, prime Risonanze.  
**Scenario:** *Notte al Monumentale*, dalla preparazione al climax.  
**Output:** problemi di comprensione e prima autonomia nell'uso dell'Anello.

Misurare:

- tempo di creazione;
- posizione in cui vengono cercate le regole;
- tempi di formulazione e scelta dei prezzi;
- rifiuti/accettazioni;
- uso dell'Ancora;
- capacità di ricostruire l'ordine Fato → eleggibilità → prezzi → scelta → esito → prezzo.

Queste due sessioni possono produrre parte dell'evidenza G2-A, ma soltanto se il Custode è indipendente dalla scrittura.

## Blocco B — Sessioni 3–4

**Focus:** combattimento, reazioni, Escalation.  
**Output:** log round e danni.

S03 usa quattro Guardiani, un avversario maggiore e minion combinati. S04 prolunga intenzionalmente uno scontro fino ai round 3–5+ per osservare Escalation.

Misurare:

- budget di Azione Significativa per unità;
- attivazioni duplicate;
- reazioni difensive/offensive;
- dubbi sull'ordine;
- Escalation su singolo, area, multi-colpo, persistente ed evocazioni;
- durata e danno per round.

Se condotte da due Custodi indipendenti, queste sessioni possono fornire G2-B/C.

## Blocco C — Sessioni 5–6

**Focus:** indagine e Linee Ley.  
**Output:** chiarezza di posizione/effetto.

S05 usa un mistero con almeno tre vie verso l'indizio fondamentale. S06 mette il gruppo tra due Linee e un Nexus senza concedere bonus numerici locali.

Misurare:

- se l'indizio fondamentale viene sempre ottenuto;
- qualità/costo di 7–9 e 6−;
- se Linee/Nexus modificano realmente accesso, posizione, effetto e informazione;
- se qualcuno tenta spontaneamente di cercare bonus numerici locali;
- quale elemento concreto di Milano influenza davvero le decisioni.

## Blocco D — Sessioni 7–8

**Focus:** stress test delle Casate.  
**Output:** economia delle risorse.

### S07 — Mictlan senza guaritore

Composizione di controllo senza Avalon/Ife dedicati alla cura. Tre scene di attrito. Registrare PF spesi, Sangue Tenace, rinunce all'uso di poteri e recupero.

### S08 — Mictlan con Avalon/Ife

Boss + recupero. Confrontare sostenibilità Mictlan, cure e centralità di Avalon/Ife. Inserire un Avalon con CAR +3 per il test B6.

## Blocco E — Sessioni 9–10

**Focus:** downtime, recupero, relazioni.  
**Output:** cicli e conseguenze.

- S09 parte con Umbra a Corruzione 0 e usa un'infiltrazione lunga.
- S10 parte con Umbra a Corruzione 6 e forza scelte ad alta pressione.

Misurare:

- Corruzione iniziale/finale;
- poteri evitati per paura del costo;
- quota di costo recuperata troppo facilmente;
- tentativi di ciclo di guarigione/Stress;
- Condizioni dell'Anello e loro risoluzione;
- Legami realmente messi in gioco.

## Blocco F — Sessioni 11–12

**Focus:** mini-arco e boss.  
**Output:** persistenza, payoff e carico del Custode.

Le due sessioni devono condividere almeno un Frammento, una fazione, un cambiamento del Velo e una conseguenza di Risonanza. Il boss finale deve poter essere negoziato, contenuto, aggirato o sconfitto: l'eliminazione non è l'unico obiettivo.

Misurare:

- conseguenze che ritornano nella fiction;
- Velo e promesse/debiti;
- carico di preparazione del Custode;
- payoff dei Legami e dell'Anello;
- distribuzione dello spotlight;
- desiderio di continuare con lo stesso personaggio.

## Matrice minima B1–B8

| Test | Ipotesi | Sessioni preparate |
|---|---|---|
| B1 | gruppo misto standard | S01, S02, S05, S06, S11, S12 |
| B2 | Mictlan senza guaritore | S07 |
| B3 | Mictlan + Avalon | S04, S08 |
| B4 | Umbra a Corruzione 0 | S09 |
| B5 | Umbra a Corruzione 6 | S10 |
| B6 | Avalon CAR +3 | S08 |
| B7 | Ife controllo campo | S03, S12 |
| B8 | nessun guaritore | S07 |

## Soglie decisionali

Le soglie sono trigger di revisione e richiedono dati replicati:

- oltre **35%** delle risoluzioni decisive attribuite alla stessa Casata in un gruppo da quattro per tre sessioni consecutive;
- oltre **30%** dei poteri disponibili mai considerati utili nei test dedicati;
- costo medio annullato dal recupero nella stessa scena in oltre **50%** delle attivazioni;
- presenza/assenza di un singolo guaritore che cambia di oltre **25%** l'uso dei poteri Mictlan;
- nessuna correzione su un singolo risultato anomalo senza almeno **tre osservazioni comparabili**.

## Output richiesto alla fine di ogni blocco

- bundle JSON validati;
- report di 1–2 pagine;
- issue nuove/aggiornate con evidenza;
- nessuna modifica silenziosa al regolamento;
- hash/versione esatta della build usata.

Analisi aggregata:

```bash
python3 scripts/analyze_playtest_bundles.py percorso/dei/bundle/*.json --out docs/playtest/reports
```

Il report automatico supporta il triage; non sostituisce la lettura qualitativa delle note né autorizza da solo una correzione.
