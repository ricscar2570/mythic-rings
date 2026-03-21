# Mythic Rings v3 — Repository Sorgente

Repo ufficiale del manuale **Mythic Rings v3** — gioco di ruolo di investigazione soprannaturale nella Milano contemporanea, basato su *Powered by the Apocalypse*.

## Struttura

```
mythic-rings-v3/
│
├── .github/
│   └── workflows/
│       └── build.yml          # Pipeline CI/CD automatica
│
├── chapters/                  # Sorgenti Markdown — uno per capitolo
│   ├── 01_ambientazione.md
│   ├── 02_custodi.md
│   ├── ...
│   └── 34_appendici.md
│
├── assets/
│   └── cover.png              # Copertina (opzionale)
│
├── build/
│   ├── engine.js              # Engine principale MD → DOCX
│   ├── md-parser.js           # Parser Markdown con estensioni custom
│   └── styles.js              # Design system: colori, font, dimensioni
│
├── scripts/
│   └── validate.js            # Validazione frontmatter e sintassi
│
├── dist/                      # Output build (gitignored)
│
├── package.json
└── README.md
```

---

## Build in locale

```bash
# Installa dipendenze
npm install

# Pipeline completa: pulisci → build DOCX → PDF (richiede LibreOffice)
npm run build:all

# Solo build DOCX
npm run build

# Solo conversione PDF (dopo aver già fatto build)
npm run build:pdf

# Pulisci artefatti di conversione nei .md
npm run clean

# Valida frontmatter e sintassi
npm run validate

# Watch mode: rigenera automaticamente al salvataggio dei .md
npm run watch
```

L'output viene salvato in `dist/`.

---

## PDF professionale

Il PDF viene generato da **WeasyPrint** (non da LibreOffice), che produce
output di qualità tipografica professionale direttamente dall'HTML.

### Caratteristiche del PDF
- Formato **A5**, due colonne con colonna di separazione
- Font **EB Garamond** (corpo testo) + **Cinzel** (titoli) — stile GdR moderno
- Copertina su sfondo scuro con CinzelDecorative
- Intestazioni capitolo su sfondo midnight con bordo oro
- Callout box con bordi colorati per tipo (warn, info, danger, ecc.)
- Tabelle con header Cinzel su sfondo scuro, righe alternate
- Stat block bestiario con sfondo midnight
- Numero di pagina + titolo capitolo corrente nell'header
- Sillabazione automatica, orphans/widows controllati

### Stack tipografico
| Elemento | Font |
|---|---|
| Corpo testo | EB Garamond 10pt |
| Titoli capitolo | Cinzel 18pt bold |
| Heading H1 sezione | Cinzel 13pt |
| Heading H2 | Cinzel 10.5pt |
| Heading H3 | EB Garamond 10pt bold italic |
| Header pagina | Cinzel 7pt |
| Numero pagina | EB Garamond 8pt crimson |

### Generare il PDF localmente
```bash
pip install weasyprint

# Solo PDF (presuppone che chapters/ sia già pulito)
npm run build:pdf

# Pipeline completa: clean → DOCX → HTML → PDF
npm run build:all
```

### File generati in `dist/`
| File | Formato | Uso |
|---|---|---|
| `Mythic_Rings_v3.docx` | Word | Editing, revisione, stampa offset |
| `Mythic_Rings_v3.html` | HTML | Intermedio per PDF, debug layout |
| `Mythic_Rings_v3.pdf`  | PDF  | Distribuzione digitale, print-on-demand |

---

## Sintassi Markdown — Estensioni Custom

Oltre alla sintassi Markdown standard, i capitoli supportano questi elementi speciali:

### Callout Box

```markdown
:::box[Titolo del box]{type=warn}
Testo del box. Supporta **grassetto**, *corsivo* e tabelle interne.
:::
```

**Tipi disponibili:**

| Tipo | Colore | Uso |
|---|---|---|
| `warn` | Oro | Avvisi e attenzioni |
| `info` | Blu | Informazioni supplementari |
| `tip` | Verde | Suggerimenti e best practice |
| `danger` | Rosso | Pericoli e regole critiche |
| `example` | Viola | Esempi di gioco |
| `rule` | Rosso | Regole ufficiali |
| `casata_avalon` | Blu | Contenuto Avalon |
| `casata_umbra` | Viola | Contenuto Umbra |
| `casata_ife` | Verde | Contenuto Ife |
| `casata_mictlan` | Blu notte | Contenuto Mictlan |

### Tabelle a Larghezza Piena

Le tabelle normali si adattano alla larghezza di colonna (2 colonne). Per tabelle che necessitano di più spazio:

```markdown
:::table-wide
| Colonna 1 | Colonna 2 | Colonna 3 | Colonna 4 |
|---|---|---|---|
| ... | ... | ... | ... |
:::
```

### Citazioni Narrative

```markdown
:::quote
«Le strade di Milano non perdonano i lenti.»
:::
```

### Stat Block (Bestiario)

```markdown
:::stat-block[Lupo Mannaro]
| PF | Armatura | Attacco | Danno | LS |
|---|---|---|---|---|
| 17 | 1 | +FOR | 2d6 | 4 |

**Abilità:** Rigenerazione +1d6 PF/round (non da argento). Morso maledetto.

**Debolezze:** Argento (danno ×2). Luna nuova (-2 a tutto).
:::
```

### Interruzioni

```markdown
[pagebreak]   → Nuova pagina
[colbreak]    → Nuova colonna
```

---

## Frontmatter dei Capitoli

Ogni file `.md` deve iniziare con questo blocco YAML:

```yaml
---
title: "Titolo del Capitolo"
chapter: 13              # numero capitolo (intero)
part: "Parte III — ..."  # nome della parte
epigraph: "Citazione."   # citazione d'apertura (opzionale)
tags: [tag1, tag2]       # tag (opzionali)
status: bozza            # bozza | revisione | finale
version: 3.1             # versione
---
```

---

## Pipeline CI/CD

La pipeline GitHub Actions si attiva automaticamente su ogni push a `main`.

```
push → validate → build-docx → build-pdf → release (solo su tag)
```

### Creare una release

```bash
git tag v3.1.0
git push origin v3.1.0
```

GitHub Actions genererà automaticamente DOCX e PDF, li allegherà alla release e pubblicherà le release notes.

---

## Contribuire

1. Ogni capitolo è un file `.md` separato in `/chapters/`
2. Il nome del file determina l'ordine: `01_`, `02_`, ecc.
3. Esegui `npm run validate` prima di ogni commit
4. Le PR richiedono che la build CI passi

---

## Tech Stack

- **Node.js 20+** — runtime
- **docx** — generazione Word
- **markdown-it** — parsing Markdown
- **LibreOffice** — conversione DOCX → PDF (solo in CI)
- **GitHub Actions** — pipeline automatica

---

*Mythic Rings v3.1 — «Milano non dorme mai. Nemmeno il male.»*
