# Mythic Rings — Changelog correzioni v3.2

Sessione di bug-fixing su tutti gli errori concreti rilevati. Ogni fix è stato
applicato su copia con tracciamento git e verificato con un gate (grep mirati +
lint tabelle) prima di passare al successivo.

## Decisioni canoniche adottate
- **PF Mictlan** = `28 + (FOR × 1)` (floor 28). La v3.1 `24+(FOR×2)` resta solo
  nella FAQ come riferimento storico.
- **Sangue Tenace**: soglia **40%** dei PF massimi (cap. 10 come fonte), conversione
  "metà del costo PF arrotondato per difetto, min 1 → +2 Stress".
- **Elena Marchetti**: FOR +1 → **29 PF** (la sua scheda in cap. 4 ha FOR +1; l'esempio
  in cap. 3 che la dava a 28 era incoerente con la scheda).
- **Stress 10 / Corruzione**: modello v3.2 progressivo — poteri **sospesi** (costo
  doppio + Sfidare Pericolo +FAT, su 6- esplosione 1d6), non "bloccati".
- **Escalation Die**: curva graduale v3.2 — R3 +1 tiro · R4 +1 tiro +1 danno ·
  R5 +1 tiro +1d4 · R6+ +2 tiro +1d6. Parte dal **round 3**.
- **Corruzione Umbra**: scala **0-8** (Trasformazione a 8).
- **Versione di prodotto**: unica, **v3.2**, su tutti i frontmatter.

## FIX 1 — Formula PF Mictlan unificata a 28+(FOR×1)
- `02` tabella risorse; `04` esempio generico, formula, scheda Elena (→ 29);
  `05` tabella riepilogo e esempio Ultimo Respiro (Elena → 29).
- Invariati perché già corretti: `03`, `05/365`, `10`, `29`, `31`. FAQ `32` lasciata
  come storia v3.1→v3.2.

## FIX 2 — Sangue Tenace: soglia unica 40% + correzione costo L3
- `03`/`04`: soglia 50% → 40%; esempio Elena ricalcolato (29 PF, soglia ≈ 12).
- **Bug aggiuntivo trovato**: la riga **L3** della tabella costi diceva "(1 PF + 2 Stress)"
  ma formula ed esempio impongono **2 PF** → corretta a "(2 PF + 2 Stress)".

## FIX 3 — Stress 10 / Corruzione: modello "sospesi" (non bloccati)
- `02` (cella tabella Avalon), `03` (descrizione Burnout), `05` (box interno che
  contraddiceva la riga 17 dello stesso capitolo), `06` (regola "BLOCCATI" → progressiva),
  `07` (chiarimento "Corruzione 7; Trasformazione a 8").

## FIX 4 — Escalation Die allineato alla curva graduale del cap. 20
- `05`: intro ("round 4" → "round 3"), tabella e esempio riscritti round per round.
- L'esempio incorporava il claim di probabilità errato "72% invece del 58%": corretto
  contestualmente (41,7% a +2 → 58,3% a +3).

## FIX 5 — Tabelle corrotte da conversione (8 tabelle in 6 capitoli)
Causa radice: lo step `parse_pandoc_simple_table` di `scripts/clean_chapters.py`
spezzava le celle multi-riga a larghezza fissa. Tabelle ricostruite:
- `05` tipi di danno e riepilogo risorse (dal contesto, alta certezza).
- `12` quartieri, `02` anelli, `02` confronto Custodi/Fratellanza (dal sorgente pulito
  `vecchio sito/mythic_rings_v3_completo.docx`).
- `29` glossario: ricostruito riga-per-riga dal sorgente pulito, **preservando i termini
  v3.2-only** (Nexus Secondari, Resilienza della Soglia, Velo Tracker) e le righe già
  corrette (PF, Escalation Die), con **patch Corruzione/Umbra 0-10 → 0-8**.
- `33` indice → vedi FIX 8.

## FIX 6 — Claim di probabilità (Ultimo Respiro)
- `05`: "+4 ≈ 83% / +2 → 72%" corretto in **+4 = 72,2% / +2 = 41,7%** (P(2d6+mod ≥10)).

## FIX 7 — Claim "300.000 sessioni di chaos testing"
- `05`: box rietichettato v3.2; frase fabbricata sostituita con "test di simulazione
  (Monte Carlo) e playtest".

## FIX 8 — Indice (cap. 33) riconciliato
- Numerazione capitoli sfasata (+1 da "Milano Sotterranea" in poi) e voci
  Combattimento/Escalation che puntavano a un Cap. 11 inesistente: rimappate ai file reali.
- Tabella mod (M1-M24) de-corrotta, riferimenti capitolo corretti, M1 Corruzione → 0-8,
  M4 Escalation → "Round 3+".
- Stamp v3.0/v3.1 → v3.2; riferimenti nel footer aggiornati.
- **Da ratificare**: la colonna "Sezione/Parte" è stata normalizzata con uno schema
  coerente per contenuto perché i campi `part:` nei frontmatter sono **internamente
  incoerenti** (es. Cap. 22 "Parte V" ma Cap. 21 "Parte VI"). Consigliata una
  normalizzazione separata dei `part:` nei frontmatter.

## Normalizzazione versioni
- Tutti i 33 frontmatter → `version: 3.2`; etichette "Regola v3.1" → "v3.2";
  Downtime "(v3.0)" → "(v3.2)".

## Guardrail anti-regressione
- `scripts/validate.js` esteso con invarianti v3.2: corruzione tabelle (spazi multipli),
  coerenza pipe header/righe, divieto `24+(FOR×2)` fuori FAQ, divieto modello "bloccato",
  divieto escalation "round 4 in poi", divieto Corruzione "0-10", check `version: 3.2`.
- `package.json` → `3.2.0`.
- **Root cause**: `npm run validate` ora fallisce *prima* della build se la corruzione
  rientra. Verificato che `clean_chapters.py` non ri-corrompe le tabelle GFM pulite.

## Stato finale
- `npm run validate`: **0 errori** (5 avvisi preesistenti non correlati).
- `npm run build`: DOCX completo generato (33 capitoli).
- Detector corruzione su tutto il libro: **0 tabelle corrotte**.

---

## Passata di design (criticità meccaniche + prep stampa)

- **#1 Economia delle azioni** — aggiunto box "La Finzione Guida le Azioni" (cap. 5):
  l'economia d'azione resta ma è dichiarata subordinata alla finzione, non una griglia a turni.
- **#2 FAT "god-stat"** — *scelta: nessun cambio di caratteristica di lancio* (Umbra/Ife/Mictlan
  restano +FAT). Aggiunto box "FAT è la Stat di Lancio - ed è una Scelta, non uno Sbilanciamento"
  (cap. 4) che documenta la contromisura (difesa/attacco/indagine su FOR/CUO/MEN) e il fatto che
  la formula PF v3.2 attenua già il MAD di Mictlan.
- **#3 Loop di guarigione** — aggiunto invariante "Nessuna Cura a Guadagno Netto" (cap. 5).
- **#4 Attaccare vs Usare Potere** — aggiunto box "Armi Magiche in Mischia" (cap. 6).
- **Bug residuo FIX 1** — corretto un leftover v3.1 nel box "Perché FOR è Importante per Mictlan"
  (cap. 4): "22 (24-2)" → "27 (28-1)", "4 PF / 2 poteri L2" → "2 PF / 1 potere L2". Sfuggito alla
  prima passata perché scritto "24 - 2" anziché "24+(FOR×2)".
