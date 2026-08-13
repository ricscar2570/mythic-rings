# Modello dati del playtest — v1

Questo documento chiude **P0.3 — Definire il modello dati del playtest**. Lo scopo è rendere confrontabili sessioni interne e blind playtest senza raccogliere dati personali non necessari.

## Principi

1. **Versione prima dei dati.** Ogni sessione registra la build esatta del regolamento.
2. **Anonimizzazione nativa.** Nomi, email, handle, indirizzi, data di nascita e localizzazione precisa non fanno parte del dataset.
3. **Una sessione, un bundle.** Il formato canonico è un file JSON conforme a `schema/session_bundle.schema.json`.
4. **Moduli separati al tavolo.** I CSV in `forms/` possono essere compilati durante la sessione e poi riversati nel bundle.
5. **Preferenza ≠ difetto.** I dati distinguono comprensione, comportamento osservato e gradimento.
6. **Risonanza misurata evento per evento.** Ogni offerta registra entrambi i prezzi, la scelta, il tempo di decisione e se la conseguenza torna nella fiction.
7. **Combattimento misurato per round.** L'obiettivo è rilevare ordine, azioni duplicate, Escalation, danno e consultazioni, non trasformare il tavolo in telemetria invasiva.

## ID anonimi

| Oggetto | Formato | Esempio |
|---|---|---|
| Gruppo | `GNNN` | `G001` |
| Sessione | `GNNN-SNN` | `G001-S01` |
| Giocatore | `GNNN-PNN` | `G001-P01` |
| Personaggio | `GNNN-CNN` | `G001-C01` |
| Scena | `GNNN-SNN-SCNN` | `G001-S01-SC03` |
| Evento Risonanza | `<sessione>-RNN` | `G001-S01-R02` |
| Combattimento | `<sessione>-CNN` | `G001-S01-C01` |
| Consultazione regola | `<sessione>-LNN` | `G001-S01-L03` |
| Issue di sessione | `<sessione>-INN` | `G001-S01-I01` |

Gli ID non devono contenere iniziali, nickname o altri elementi riconducibili a una persona.

## Campi obbligatori della sessione

- `schema_version`;
- `session.session_id`, `group_id`, `rules_version`, `test_mode`, `scenario_id`;
- durata e preparazione in minuti;
- numero di giocatori;
- profilo del gruppo;
- almeno un personaggio;
- array espliciti per Risonanza, combattimenti, consultazioni e issue, anche se vuoti;
- questionario post-sessione con desiderio di seconda sessione e note separate su comprensione/preferenza.

## Scheda personaggio per il test

Per ogni Guardiano si registrano:

- Casata e livello/avanzamento;
- PF, Stress, Corruzione e Fato iniziali/finali;
- nome della risorsa specifica di Casata, se applicabile, con valore iniziale/finale;
- numero di poteri usati;
- Legame scelto come Ancora (solo tipo e livello, mai identità della persona reale);
- spotlight: quante risoluzioni decisive sono attribuite al personaggio.

Questi campi consentono i confronti del piano su sostenibilità, centralità e costi delle Casate.

## Log Risonanza

Per ogni invocazione o offerta completa:

- mossa eleggibile e risultato prima della Risonanza;
- eventuale Fato usato prima;
- due prezzi dichiarati con categoria e testo;
- validità percepita di ciascun prezzo;
- scelta o rifiuto;
- risultato dopo la Risonanza;
- secondi impiegati per decidere;
- uso dell'Ancora;
- valutazione 1–5 di chiarezza, pertinenza e difficoltà reale della scelta;
- se la conseguenza è tornata concretamente nella fiction entro la sessione.

## Log combattimento

Per ogni round:

- combattimento, round e scena;
- valore di Escalation;
- azioni significative dei Guardiani;
- mosse del Custode;
- minacce ignorate che hanno agito;
- attivazioni di gruppi di minion;
- danno totale ai Guardiani e agli avversari;
- numero di consultazioni e dubbi sull'ordine;
- flag `possible_duplicate_enemy_action` quando il gruppo sospetta una doppia attivazione.

## Consultazioni delle regole

Ogni ricerca frequente registra:

- regola o termine cercato;
- dove il tester si aspettava di trovarlo;
- dove è stato trovato;
- tempo in secondi;
- se l'applicazione finale era corretta;
- eventuale issue collegata.

Questo produce direttamente la metrica “tempo mediano di consultazione inferiore a 60 secondi”.

## Dati personali e consenso

Il dataset **non richiede**:

- nome e cognome;
- email o telefono;
- handle social;
- indirizzo o città precisa;
- età esatta o data di nascita;
- audio/video della sessione;
- dati sanitari o altre categorie sensibili.

Il coordinatore può conservare separatamente un registro di consenso e contatto necessario all'organizzazione, ma tale registro non entra nel dataset di analisi e non usa gli ID per ricostruire pubblicamente l'identità dei partecipanti.

## Flusso consigliato

1. Copiare `templates/session_bundle.template.json`.
2. Assegnare ID anonimi.
3. Compilare i moduli durante la sessione.
4. Trascrivere/aggregare nel bundle JSON entro 24 ore.
5. Validare:

```bash
python3 scripts/validate_playtest_dataset.py percorso/session_bundle.json
```

6. Conservare il bundle insieme alla versione esatta del regolamento.

## Smoke test della Fase 0

`tests/fixtures/playtest_phase0_smoke/session_bundle.json` è un dataset sintetico e anonimo. Il validator deve accettarlo integralmente: dimostra che una sessione di prova può produrre un dataset completo prima dell'avvio dei test reali.
