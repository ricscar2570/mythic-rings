# Convenzioni degli identificatori — Mythic Rings

Versione convenzione: **1.0**  
Entrata in vigore: **Fase 0 / G0**

Gli ID sono stabili e non devono essere riutilizzati. Un cambio di nome, livello, quartiere o funzione non cambia l'ID dell'oggetto già esistente.

## Entità di gioco

| Entità | Formato | Esempio | Regola |
|---|---|---|---|
| Regola | `MR-RULE-NNN` | `MR-RULE-015` | Sequenza globale; già in uso nella specifica canonica. |
| Potere Avalon | `MR-PWR-AVA-NNN` | `MR-PWR-AVA-001` | Il numero non incorpora il livello, che può cambiare. |
| Potere Umbra | `MR-PWR-UMB-NNN` | `MR-PWR-UMB-001` | Come sopra. |
| Potere Ife | `MR-PWR-IFE-NNN` | `MR-PWR-IFE-001` | Come sopra. |
| Potere Mictlan | `MR-PWR-MIC-NNN` | `MR-PWR-MIC-001` | Come sopra. |
| PNG | `MR-NPC-NNN` | `MR-NPC-001` | Non codificare Casata o ruolo nell'ID. |
| Luogo / Nexus | `MR-LOC-NNN` | `MR-LOC-001` | Quartiere e funzione restano attributi modificabili. |
| Avversario / creatura | `MR-ADV-NNN` | `MR-ADV-001` | L'ID resta anche se cambia il nome editoriale. |
| Fazione | `MR-FAC-NNN` | `MR-FAC-001` | Riservato alla canonizzazione del mondo. |

`NNN` è sempre a tre cifre, parte da `001` e non viene riciclato dopo una rimozione.

## Issue e decisioni

Le issue usano un prefisso di categoria, separato dalla priorità:

| Categoria | Formato | Uso |
|---|---|---|
| Canon | `CANON-NNN` | Lore, cronologia, geografia, PNG, istituzioni. |
| Regole | `RULE-NNN` | Procedure normative e casi limite. |
| Bilanciamento | `BAL-NNN` | Ipotesi da misurare e correzioni quantitative. |
| Playtest | `PT-NNN` | Protocollo, campione, strumenti o risultati. |
| Editoriale | `EDIT-NNN` | Struttura, terminologia, lingua, navigazione. |
| Produzione | `PROD-NNN` | Build, tabelle, artefatti, accessibilità, stampa. |
| Legale / diritti | `LEGAL-NNN` | Licenze, marchi, privacy, crediti. |
| Commerciale | `MKT-NNN` | Prezzo, conversione, canali, validazione mercato. |

La priorità (`P0`–`P3`) è un campo separato e può cambiare senza cambiare l'ID.

Le decisioni aperte usano `DEC-NNN`; le decisioni già adottate e normative continuano a essere documentate come ADR (`ADR-NNN-*`).

## Riferimenti al piano

Gli ID `P0-01`, `P1-03` ecc. del piano di sviluppo vengono conservati nel campo `roadmap_ref` del registro issue. Non sostituiscono l'ID stabile della issue.

## Assegnazione

1. Cercare nel registro se l'entità/issue esiste già.
2. Usare il primo numero libero della categoria.
3. Non rinumerare dopo merge, split o chiusura.
4. In caso di duplicato, mantenere l'ID più antico e inserire l'altro in `merged_refs`.
5. Ogni ID introdotto nel manoscritto deve essere aggiunto alla sua fonte strutturata o al registro proprietario previsto dalla fase competente.
