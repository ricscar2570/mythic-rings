# Mythic Rings — Repository editoriale

Repository sorgente di **Mythic Rings: Guardiani di Milano**, gioco di ruolo urban fantasy narrativo e tattico basato su 2d6, scritto da **Riccardo Scaringi**.

Stato attuale: **0.9.0-beta.2**. La beta è adatta a build, revisione e playtest; non è ancora autorizzata come release commerciale 1.0 perché restano obbligatori i gate esterni descritti in `docs/RELEASE_GATES.md`.

## Identità del prodotto

I giocatori interpretano Guardiani scelti dagli Anelli mitici delle quattro Casate. Proteggono il Velo nella Milano contemporanea, indagano minacce e fazioni, e usano poteri che consumano Stress, Corruzione o Punti Ferita. Soltanto i giocatori tirano i dadi; il combattimento usa PF, Armatura, distanze narrative ed Escalation applicata al danno. **Quando i dadi non bastano, un Guardiano può far risuonare l'Anello e migliorare l'esito accettando un prezzo su Corpo, Anima, Legami o Velo:** questa è la meccanica-identità della beta.2.

## Fonte di verità

Le regole fondamentali seguono questa gerarchia:

1. `data/canonical_rules.yml`;
2. `docs/CANONICAL_RULES_SPEC.md`;
3. capitoli normativi del manuale;
4. quick reference, FAQ e prodotti derivati.

Il **canon di mondo** segue una gerarchia parallela:

1. `data/canon/world.yml`, `occult_geography.yml`, `npcs.yml`, `timeline.yml`;
2. `docs/CANON_BIBLE.md` e viste di consultazione derivate;
3. capitoli del manuale e campagna;
4. prodotti derivati.

Una release candidata non può contenere divergenze tra questi livelli. Le decisioni meccaniche significative richiedono un ADR in `docs/decisions/` e test aggiornati.

Il bestiario deriva da `data/adversaries.yml`; non modificare direttamente gli stat block generati senza aggiornare la fonte.

## Struttura

```text
.
├── book.yml                         # metadati, versione e ordine dei capitoli
├── chapters/                        # 33 capitoli Markdown del manuale
├── data/
│   ├── canonical_rules.yml          # regole canoniche
│   ├── adversaries.yml              # sorgente strutturata del bestiario
│   └── toc-pages.lock.json          # paginazione verificata dell’indice
├── products/
│   ├── quickstart/                  # quickstart e modulo di feedback
│   ├── player-kit/                  # scheda, tracker e riferimenti
│   └── adventure/                   # Notte al Monumentale autonoma
├── docs/                             # specifiche, gate, playtest, legale e lancio
│   ├── project/                     # issue, decisioni, changelog master e convenzioni ID
│   ├── playtest/                    # modello dati, schema e moduli di raccolta
│   └── gates/                       # report verificabili dei gate della roadmap
├── build/                            # renderer DOCX, HTML e PDF
├── scripts/                          # generatori, audit e preflight
├── tests/                            # test delle regole canoniche
├── .github/                          # CI e template delle issue
└── dist/                             # artefatti generati, non sorgenti
```

## Requisiti

- Node.js 18 o superiore;
- Python 3.10 o superiore;
- LibreOffice;
- Pandoc;
- dipendenze Python indicate in `requirements.txt`.

Installazione:

```bash
npm ci
python3 -m pip install -r requirements.txt
```

`npm ci` materializza automaticamente in `assets/fonts/` i font web definiti dalle dipendenze `@fontsource`; i binari non sono parte del pacchetto sorgente.

## Comandi principali

```bash
# Rigenera il bestiario, valida corpus, test canonici, governance, canon G1 e consolidamento tecnico delle regole Fase 2
npm run verify

# Verifica soltanto baseline, registri e fixture del modello dati playtest
npm run phase0:check

# Verifica la Fase 0 e il canon di mondo chiuso a G1
npm run phase1:check

# Verifica G0 + G1 + coerenza tecnica delle regole candidate G2
npm run phase2:check

# Verifica che il piano delle 12 sessioni interne sia completo senza confonderlo con evidenza reale
npm run playtest:plan:check

# Costruisce il manuale usando il lock di paginazione già committato
npm run build:manual

# Ricostruisce il manuale e rigenera/stabilizza il lock dell'indice
npm run build:manual:refresh

# Costruisce quickstart, kit e avventura autonoma
npm run build:products

# Pulisce e ricostruisce tutti gli artefatti usando il lock esistente
npm run build:all

# Pulisce, ricostruisce tutto e rigenera il lock di paginazione
npm run build:all:refresh

# Verifica sorgenti e artefatti già costruiti, senza ricostruirli
npm run release:preflight

# Gate beta/CI autosufficiente: refresh della paginazione, build completa e preflight
npm run release:check

# Gate RC/1.0: usa il lock già committato e fallisce se la paginazione diverge
npm run release:locked

# Alias del gate beta/CI
npm run release:build
```

Gli artefatti vengono scritti in `dist/` e `dist/products/`.


## Governance della roadmap

La **Fase 0** è chiusa in `docs/gates/G0_BASELINE_FROZEN.md` e la **Fase 1** in `docs/gates/G1_CANON_APPROVED.md`. La **Fase 2** ha raggiunto una *rules-lock candidate* verificata tecnicamente, documentata in `docs/gates/G2_RULES_LOCK_CANDIDATE.md`, ma **G2 non è ancora PASS**: restano le evidenze umane su formulazione dei prezzi, ordine del round e Sangue Tenace definite in `docs/playtest/PHASE2_RULES_TEST_SCRIPT.md`. La baseline 0.9.0-beta.2 è congelata sotto `archive/baselines/0.9.0-beta.2/`; issue e decisioni sono gestite in `docs/project/`, il modello dati dei playtest è in `docs/playtest/` e il canon strutturato di mondo è in `data/canon/`.

Ogni modifica successiva deve citare un ID stabile del registro o un ADR. Gli ID del piano (`P0-01`, `P1-03` ecc.) restano riferimenti di roadmap e non sostituiscono gli ID stabili `CANON-*`, `RULE-*`, `BAL-*` ecc.

La preparazione della **Fase 3** è descritta in `docs/playtest/PHASE3_INTERNAL_PLAYTEST_PLAN.md` e `data/playtest/phase3_internal_plan.yml`: 12 sessioni in sei blocchi A–F, matrice B1–B8 e soglie decisionali. Lo stato è intenzionalmente `prepared_not_executed`; il repository non deve mai trasformare fixture o simulazioni in evidenza di playtest reale. I bundle reali possono essere aggregati con `python3 scripts/analyze_playtest_bundles.py ... --out docs/playtest/reports`.

## Pipeline di produzione

`release:check` è intenzionalmente autosufficiente per beta e CI: funziona dopo un checkout pulito, ricostruisce `dist/` e **rigenera il lock di paginazione** quando il testo è cambiato. `release:preflight` controlla invece artefatti già costruiti. `release:locked` è il gate più severo per RC/1.0: usa il lock già committato e fallisce se la paginazione effettiva diverge.

La pipeline `release:check` esegue:

1. controllo di portabilità della repository;
2. generazione del bestiario strutturato;
3. validazione di frontmatter, versione e sintassi;
4. test delle regole canoniche e audit semantico;
5. generazione del manuale DOCX;
6. generazione HTML;
7. rigenerazione iterativa del lock di paginazione fino alla stabilità;
8. conversione del DOCX in PDF tramite LibreOffice;
9. post-processing PDF atomico con metadati e segnalibri;
10. generazione dei prodotti separati;
11. preflight su file, pagine, metadati, placeholder e parità approssimativa.

Il PDF ufficiale non dipende da WeasyPrint. Per lavoro quotidiano, `build:manual` e `build:all` conservano la modalità rapida a lock già noto; se il testo cambia la paginazione possono chiedere di eseguire `build:pdf:refresh`. Prima di una release candidate esegui un refresh, **committa `data/toc-pages.lock.json`**, quindi verifica da checkout pulito con `npm run release:locked`. La precedente pipeline WeasyPrint è soltanto codice storico e non è il percorso di release.

## Prodotti generati

### Manuale base

```text
Mythic_Rings_Prima_Edizione_beta2.docx
Mythic_Rings_Prima_Edizione_beta2.html
Mythic_Rings_Prima_Edizione_beta2.pdf
```

### Prodotti di ingresso

```text
Mythic_Rings_Quickstart_beta2.*
Mythic_Rings_Kit_del_Giocatore_beta2.*
Mythic_Rings_Notte_al_Monumentale_beta2.*
```

Il quickstart contiene regole essenziali, quattro pregenerati e l'avventura. L'avventura autonoma ripropone lo scenario come fascicolo separato con handout, gestione del ritmo e rapporto di playtest.

## Style guide e terminologia

La grafia normativa è in `docs/EDITORIAL_STYLE_GUIDE.md`. In particolare, **Custode** al singolare indica soltanto il GM; **i Custodi di Milano** è il nome collettivo dell'organizzazione e i suoi singoli membri sono **Guardiani**. Le distanze canoniche sono **Contatto, Vicino, Lontano, Remoto**.

## Sintassi editoriale

### Box

```markdown
:::box[Titolo]{type=warn}
Contenuto.
:::
```

Tipi principali: `warn`, `info`, `tip`, `danger`, `example`, `rule`, `casata_avalon`, `casata_umbra`, `casata_ife`, `casata_mictlan`.

### Stat block

Gli stat block del manuale vengono generati da `data/adversaries.yml` e seguono il principio player-facing: PF, Armatura, danno, impulso, tag, mosse e debolezze; nessuna statistica Attacco del Custode.

### Interruzioni

```markdown
[pagebreak]
[colbreak]
```

## Regole di contribuzione

Leggere `CONTRIBUTING.md`. In sintesi:

- non correggere una regola soltanto nella FAQ o nel quick reference;
- non aggiungere statistiche di Attacco agli avversari;
- non superare i limiti canonici di modificatori e Armatura;
- non introdurre azioni extra tramite Punti Fato;
- non dichiarare la versione 1.0 senza gate esterni documentati;
- eseguire `npm run verify` prima di ogni commit.

## Gate ancora esterni

La repository non può certificare autonomamente:

- blind playtest indipendente;
- developmental e technical editing indipendenti;
- lettura culturale delle tradizioni rappresentate;
- verifica legale di nome, licenze, font e contributi;
- verifica fiscale e dei canali di vendita;
- validazione commerciale tramite quickstart.

Il successo commerciale non è garantibile da una build. La repository riduce i rischi editoriali e tecnici; la versione finale resta subordinata ai dati dei playtest e alle verifiche professionali.

## Licenza

Lo stato dei diritti è descritto in `LICENSE-PENDING.md` e `docs/RIGHTS_REGISTER.csv`. Fino alla verifica finale, nessun contenuto della repository deve essere considerato open source o riutilizzabile automaticamente.
