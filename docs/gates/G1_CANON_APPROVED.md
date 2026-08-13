# Gate G1 — Canon approvato

**Versione:** 0.9.0-beta.2  
**Data:** 13 agosto 2026  
**Esito:** **PASS**  
**Fase:** 1 — Canonizzazione del mondo

## Mandato del gate

G1 chiude le incompatibilità interne su geografia occulta, PNG ricorrenti, cronologia e scale organizzative prima che il regolamento venga nuovamente consolidato. Non autorizza ancora la release commerciale e non sostituisce sensitivity reading, verifica legale o blind playtest.

## Evidenze C1.1 — Linee Ley e Nexus

- Fonte strutturata: `data/canon/occult_geography.yml`.
- Cinque Linee canoniche con ID MR-LEY-001..005 e un unico percorso ciascuna.
- Nexus del Duomo MR-LOC-001 + cinque Nexus Secondari MR-LOC-002..006.
- Ogni Nexus possiede funzione, custodia, rischio, beneficio e segnale sensoriale.
- `numeric_roll_modifiers: false`: Linee e Nexus agiscono su accesso, posizione, effetto, scala, informazione e rischio fictionale, non su bonus/malus generici.
- I capitoli 1, 3, 11 e 12 sono stati riallineati.
- `scripts/validate_world_canon.py` impedisce la regressione dei percorsi e dei vecchi pacchetti locali noti.

**P0 chiuso:** CANON-001 e CANON-004.

## Evidenze C1.2 — Custodi e PNG ricorrenti

Fonte strutturata: `data/canon/npcs.yml`; vista rapida: `docs/CANON_ROSTER.md`.

Gerarchia canonica:

1. Elisabetta Conti — Presidente neutrale della Cerchia, ex-Avalon ritirata.
2. Eleonora Visconti — Anziana Avalon e coordinatrice operativa.
3. Leila Ferrara — Anziana Umbra.
4. Kwame Asante — Anziano Ife.
5. Marisol Reyes — Anziana Mictlan.
6. Padre Tommaso De Luca — Guardiano Avalon veterano e mentore, non Anziano.
7. Valentina Riva, «La Volpe» — Umbra rinnegata e mediatrice indipendente.

I PNG canonici non vengono più usati come pregenerati.

**P0 chiuso:** CANON-002.

## Evidenze C1.3 — Cronologia e origine delle Casate

- Fonte strutturata: `data/canon/timeline.yml`.
- Cronologia di 12 eventi: prima del 1224 → oggi.
- Le quattro **stirpi di Anelli** sono più antiche delle istituzioni; i nomi moderni Avalon, Umbra, Ife e Mictlan sono categorie istituzionali applicate retroattivamente.
- Il 1224 resta data fittizia della fondazione dei Custodi ma non viene più descritto come anno in cui Milano sarebbe stata “devastata dalle guerre di Federico II”.
- 1386 resta il riferimento storico all'avvio del cantiere del Duomo; Patto del Nexus, frattura e Frammenti sono esplicitamente fiction.
- Il 1630 non attribuisce più protocolli al Cimitero Monumentale, che è un'istituzione ottocentesca.
- Rimosse le vecchie formule che facevano “arrivare” Ife nel Seicento e Mictlan nell'Ottocento tramite migrazioni inventate.
- La verifica culturale specialistica resta obbligatoria in `LEGAL-001` prima della release commerciale.

**P0 chiuso:** CANON-003.

## Evidenze C1.4 — Numeri e istituzioni

Fonte strutturata: `data/canon/world.yml`.

- Comune di Milano: testo arrotondato a circa 1,4 milioni; dato di riferimento 1.399.079 residenti al 31/12/2025.
- Città Metropolitana: testo arrotondato a circa 3,25 milioni; dato di riferimento 3.246.455 residenti al 01/01/2025.
- Custodi: circa 40 Guardiani attivi + circa 200 persone di supporto interno.
- Società del Velo: circa 100 operativi e organizzazione distinta.
- Cerchia: cinque seggi.
- Anelli attivi: circa 40; i “quattro Anelli” rituali indicano le quattro stirpi, non quattro soli artefatti.

Le fonti di ricerca e la distinzione fatto reale / elemento fittizio sono documentate in `docs/research/CANON_SOURCE_NOTES.md`.

## Decisioni G1

Tutte le otto decisioni richieste al lead designer sono registrate come `accepted` in `docs/project/DECISION_REGISTER.csv`:

- DEC-001 — presente mobile (“Milano, oggi”);
- DEC-002 — Elisabetta ed Eleonora coesistono con ruoli distinti;
- DEC-003 — stirpi precedenti, Casate moderne;
- DEC-004 — Linee/Nexus solo fiction-posizione-effetto;
- DEC-005 — direzione prodotto Ring Core + Guardiani di Milano, con separazione materiale dopo G4;
- DEC-006 — Rinuncia: conseguenze permanenti solo con consenso e procedura espliciti;
- DEC-007 — target +2: circa 83,3% di 7+ e 41,7% di 10+ prima di Fato/Risonanza;
- DEC-008 — invarianti identitari del prodotto fissati.

Le decisioni restano modificabili esclusivamente tramite change request registrata.

## Controlli eseguiti

```text
python3 scripts/validate_world_canon.py
Gate G1 — canon valido.
  Linee Ley: 5
  Nexus: 1 centrale + 5 secondari
  PNG ricorrenti canonici: 7
  Cronologia: 12 eventi
  Bonus locali generici Linee/Nexus: vietati e non rilevati
  Formulazioni storiche/culturali P0 obsolete: non rilevate nel corpus user-facing
```

`npm run phase1:check` esegue anche tutti i controlli G0 prima del controllo canonico.

## Limiti espliciti del PASS

G1 certifica **coerenza interna e tracciabilità del canon**, non accuratezza culturale definitiva o accettazione del mercato. Restano aperti:

- `LEGAL-001` — sensitivity reading Ife/Mictlan;
- `CANON-005` — verifica geografica/storica estesa di Milano;
- `LEGAL-002` — verifica legale;
- tutti i gate di playtest e produzione successivi.

## Decisione

**GO a Fase 2 — Consolidamento delle regole.** Nessun nuovo sottosistema viene autorizzato. Le modifiche successive devono utilizzare il canon G1 come vincolo.
