# Mythic Rings — Repository editoriale

Repository sorgente di **Mythic Rings: Guardiani di Milano**, gioco di ruolo urban fantasy narrativo e tattico basato su 2d6, scritto da **Riccardo Scaringi**.

Stato attuale: **0.9.0-beta.1**. La beta è adatta a build, revisione e playtest; non è ancora autorizzata come release commerciale 1.0 perché restano obbligatori i gate esterni descritti in `docs/RELEASE_GATES.md`.

## Identità del prodotto

I giocatori interpretano Guardiani scelti da quattro Anelli mitici. Proteggono il Velo nella Milano contemporanea, indagano minacce e fazioni, e usano poteri che consumano Stress, Corruzione o Punti Ferita. Soltanto i giocatori tirano i dadi; il combattimento usa PF, Armatura, distanze narrative ed Escalation applicata al danno.

## Fonte di verità

Le regole fondamentali seguono questa gerarchia:

1. `data/canonical_rules.yml`;
2. `docs/CANONICAL_RULES_SPEC.md`;
3. capitoli normativi del manuale;
4. quick reference, FAQ e prodotti derivati.

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
# Rigenera il bestiario, valida il corpus ed esegue i test
npm run verify

# Costruisce manuale DOCX, HTML e PDF
npm run build:manual

# Costruisce quickstart, kit e avventura autonoma
npm run build:products

# Pulisce e ricostruisce tutti gli artefatti
npm run build:all

# Rigenera il lock dell’indice dopo modifiche che cambiano la paginazione
npm run build:pdf:refresh

# Verifica sorgenti e artefatti già costruiti, senza ricostruirli
npm run release:preflight

# Gate di release: pulizia, ricostruzione completa e preflight
npm run release:check

# Alias esplicito del gate di release
npm run release:build
```

Gli artefatti vengono scritti in `dist/` e `dist/products/`.

## Pipeline di produzione

`release:check` è intenzionalmente autosufficiente: funziona anche dopo un checkout pulito, quando `dist/` non esiste. `release:preflight` è invece il controllo rapido per artefatti già costruiti.

La pipeline completa esegue:

1. generazione del bestiario strutturato;
2. validazione di frontmatter, versione e sintassi;
3. test delle regole canoniche;
4. audit semantico dei contenuti;
5. generazione del manuale DOCX;
6. generazione HTML;
7. caricamento del lock di paginazione dell’indice;
8. conversione del DOCX in PDF tramite LibreOffice;
9. confronto tra pagine effettive e lock: la build fallisce se l’indice è obsoleto;
10. post-processing PDF atomico con metadati e segnalibri;
11. generazione dei prodotti separati;
12. preflight su file, pagine, metadati, placeholder e parità approssimativa.

Il PDF ufficiale non dipende da WeasyPrint. La build ordinaria usa un solo passaggio e rifiuta un indice non più allineato. `npm run build:pdf:refresh` esegue i passaggi lenti necessari a stabilizzare e aggiornare il lock soltanto dopo modifiche che alterano la paginazione. La precedente pipeline WeasyPrint è conservata soltanto come codice storico e non è il percorso di release.

## Prodotti generati

### Manuale base

```text
Mythic_Rings_Prima_Edizione_beta1.docx
Mythic_Rings_Prima_Edizione_beta1.html
Mythic_Rings_Prima_Edizione_beta1.pdf
```

### Prodotti di ingresso

```text
Mythic_Rings_Quickstart_beta1.*
Mythic_Rings_Kit_del_Giocatore_beta1.*
Mythic_Rings_Notte_al_Monumentale_beta1.*
```

Il quickstart contiene regole essenziali, quattro pregenerati e l'avventura. L'avventura autonoma ripropone lo scenario come fascicolo separato con handout, gestione del ritmo e rapporto di playtest.

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
