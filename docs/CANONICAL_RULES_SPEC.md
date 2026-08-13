# Mythic Rings — Canonical Rules Specification

Questa specifica è il secondo livello della fonte normativa del sistema. In caso di divergenza, `data/canonical_rules.yml` prevale; questa specifica traduce gli invarianti che manuale, quick reference, FAQ e prodotti derivati devono rispettare.

## Principi di canonizzazione

1. Una regola completa compare in un solo punto normativo e le sue sintesi devono essere semanticamente equivalenti.
2. Le sintesi non possono introdurre eccezioni.
3. Il Custode non tira dadi per gli avversari.
4. I modificatori non devono cancellare stabilmente la fascia 7–9.
5. L'Anello può cambiare un esito soltanto attraverso **Risonanza** e un prezzo dichiarato, mai come bonus nascosto.
6. Un indizio necessario non è mai negato da un singolo tiro.
7. Le risorse non possono essere recuperate tramite cicli a guadagno netto.
8. Ogni eccezione deve indicare esplicitamente la regola che modifica.

## Regole canoniche

Le regole **MR-RULE-001 — MR-RULE-018** sono definite integralmente in `data/canonical_rules.yml`. Ogni modifica richiede:

- un ADR in `docs/decisions/`;
- aggiornamento dei capitoli normativi e dei prodotti derivati;
- aggiornamento dei test e degli audit;
- incremento di versione quando cambia il comportamento al tavolo.

## Invarianti Ring Core — beta.2

### MR-RULE-015 — Risonanza dell'Anello

- **Eleggibilità:** soltanto **Usare Potere** e le **Mosse Esclusive di Casata che richiedono un tiro**.
- **Momento:** dopo eventuale Fato e prima delle conseguenze del risultato finale.
- **Frequenza:** una volta per scena per Guardiano. Una scena è un'unità continua di luogo, tempo e obiettivo immediato; non si resetta per round, pausa breve, spostamento tattico o ambiente adiacente mentre il conflitto resta lo stesso. Il Custode chiarisce i casi dubbi prima del tiro successivo.
- **Upgrade:** 6− → 7–9 oppure 7–9 → 10+.
- **Eccezioni:** il 2 naturale non migliora; si controlla sui due dadi finali dopo eventuale Fato. Ultimo Respiro, downtime, azioni mondane e poteri senza tiro non sono eleggibili.
- **Prezzo:** il Custode offre due categorie differenti, realmente valide, e dichiara per intero entrambi i prezzi. Se non può formularne due, la procedura non parte e l'uso resta disponibile. Dopo la dichiarazione completa di due prezzi validi, l'uso della scena è speso anche in caso di rifiuto; il giocatore ne accetta uno oppure mantiene il risultato originale.
- **Ordine:** si risolve l'esito migliorato e subito dopo si applica il prezzo, prima di una nuova azione.
- **Nessuna doppia conseguenza:** non si applica anche la conseguenza dell'esito originale migliorato; il costo base del potere già pagato resta invece pagato.

Categorie canoniche:

- **Corpo:** −4 PF ignorando Armatura, non riducibili/convertibili/trasferibili; può attivare Ultimo Respiro dopo l'effetto.
- **Anima:** Condizione dell'Anello nuova o significativamente diversa, con limite concreto e via di risoluzione giocabile.
- **Legame:** conseguenza concreta su un Legame L1+ raggiungibile dalla fiction; nessuna perdita automatica di livello.
- **Mondo:** Velo Tracker +1 e una traccia reale; non è disponibile a Velo 12 salvo procedura di campagna esplicita oltre la Rivelazione.

I due prezzi devono essere **entrambi realmente applicabili** e non possono duplicare un costo obbligatorio già pagato per lo stesso tiro. La libreria operativa `data/risonanza_price_examples.yml` / `docs/rules/RISONANZA_PRICE_LIBRARY.md` contiene 6 esempi per ciascuna Casata e categoria: è materiale di supporto, non una seconda fonte normativa.

### MR-RULE-016 — Ancora dell'Anello

- Alla creazione si designa un **Legame L1+** come Ancora.
- Non concede bonus numerici.
- Una volta per sessione, se l'Ancora è direttamente presente o in contatto significativo e viene offerto **Anima**, il giocatore può chiedere di sostituire quel prezzo con **Legame** sull'Ancora; se l'altro prezzo era già Legame, questa è l'unica eccezione alle categorie differenti e le due conseguenze devono restare materialmente diverse.
- Il Custode dichiara il nuovo prezzo prima della scelta.
- Se l'Ancora scende a L0 o viene spezzata, una nuova Ancora richiede una scena significativa e non può essere scelta nel mezzo della stessa risoluzione.

### MR-RULE-012 — Stress, Burnout e verbi delle risorse

- **Subire X Stress** aumenta il tracker; **recuperare X Stress** lo riduce.
- **Spendere X PF** è un costo volontario e non è danno; **subire danno** segue Armatura e tipo; **perdere PF** è una perdita diretta soltanto quando una regola la dichiara.
- A Stress 8–9 i poteri con costo in Stress costano 1 Stress aggiuntivo.
- Stress non supera 10. Calcola il costo finale: ogni punto che eccederebbe 10 diventa **sovraccarico**, fa perdere 2 PF ignorando Armatura e attiva Sfidare il Pericolo +FAT prima del tiro del potere.
- Su 10+ del Burnout si procede; su 7–9 si procede con costo/posizione/esposizione immediata che non sia altro Stress; su 6− si subiscono 1d6 danni puri e l'effetto desiderato non si produce. Il costo già pagato resta pagato.
- Un costo «porta lo Stress a 10» riempie il tracker; se il Guardiano è già a 10, conta come 1 punto di sovraccarico.

### MR-RULE-013 — Sangue Tenace

- Una volta per scena, dopo avere calcolato il costo finale in PF e prima di spenderlo.
- Si attiva soltanto se il pagamento integrale lascerebbe il Guardiano **sotto** il 40% dei PF massimi; il 40% esatto non basta.
- Il costo deve essere almeno 2 PF e il Guardiano deve poter subire interamente 2 Stress (Stress iniziale 0–8).
- PF convertiti = `floor(costo / 2)`, minimo 1 e massimo `costo - 1`; il residuo resta quindi almeno 1 PF.
- Si spendono i PF residui e si subiscono 2 Stress. Armatura/resistenze non modificano i costi; riduzioni esplicite del costo si applicano prima. Corpo della Risonanza non è convertibile.

### MR-RULE-017 — Stati del legame con l'Anello

1. **Anello tolto:** il legame resta integro e non compaiono penalità.
2. **Separazione temporanea:** di norma poteri/Risonanza/Ancora restano disponibili; una soppressione fictionale deve essere specifica e dichiarata prima del tiro.
3. **Cessione:** affidare l'oggetto non trasferisce scelta o poteri; per il portatore vale come separazione temporanea.
4. **Rinuncia:** procedura volontaria di campagna con consenso preventivo; dopo il rituale si perdono poteri di Casata, Risonanza e Ancora. Nessuna penalità permanente ulteriore viene improvvisata.

La morte è una rottura separata. Togliere, separare o cedere l'Anello non evita costi/prezzi già dichiarati e non resetta la scena.

### MR-RULE-018 — Velo Tracker

- Unica scala globale: **0–12**. Non esiste una seconda scala meccanica Esposizione 0–4.
- Soglie: 3 Voci, 6 Sospetto, 9 Crisi d'Identità, 12 Velo Squarciato.
- Il prezzo Mondo avanza sempre di +1 e nomina una traccia reale; non si somma un secondo +1 per la stessa prova.
- Dopo avere raggiunto 6/9/12, il nuovo minimo permanente è 3/6/9.

### MR-RULE-008 — Budget delle minacce

Una minaccia singola o un gruppo di minion gestito come unità possiede normalmente **una Azione Significativa per round**. Danno pieno, Condizione, spostamento forzato, presa di obiettivo o Mossa offensiva nominata spendono il budget. A fine round agiscono soltanto le unità che non l'hanno già speso. `docs/rules/COMBAT_ROUND_EXAMPLE.md` mostra il caso completo con quattro Guardiani, due minion combinati e una minaccia maggiore.

### MR-RULE-009 — Fonte dell'Escalation

L'Escalation si applica **al massimo una volta per Azione Principale del Guardiano che infligge danno**. Area e multi-colpo scelgono una sola istanza o un solo bersaglio. Attacchi bonus, reazioni, danni persistenti e azioni autonome di evocazioni non ricevono il bonus senza una Azione Principale spesa dal Guardiano. I cinque casi limite sono in `docs/rules/ESCALATION_CASES.md`.

La beta.2 non presume che questa configurazione sia già bilanciata. I criteri quantitativi e le varianti di fallback sono definiti in `docs/RING_CORE_BALANCE_MODEL.md` e devono essere verificati nel blind playtest prima della 1.0.

## Gerarchia delle fonti

1. `data/canonical_rules.yml`;
2. `docs/CANONICAL_RULES_SPEC.md`;
3. capitolo 5, *Come si gioca*;
4. capitolo 6, *Mosse base*;
5. capitoli delle Casate e dei poteri;
6. quick reference e prodotti derivati;
7. FAQ.

La gerarchia serve per diagnosticare una regressione, non per giustificarla. Una release candidata non deve contenere divergenze tra questi livelli.
