# Mythic Rings - Canonical Rules Specification

Questa specifica e la fonte normativa del sistema. In caso di divergenza, `data/canonical_rules.yml` e questo documento prevalgono sul manuale, sulle FAQ e sui riferimenti rapidi fino alla successiva sincronizzazione.

## Principi di canonizzazione

1. Una regola completa compare in un solo punto normativo.
2. Le sintesi non possono introdurre eccezioni.
3. Il Custode non tira dadi per gli avversari.
4. I modificatori non devono cancellare stabilmente la fascia 7-9.
5. Un indizio necessario non e mai negato da un singolo tiro.
6. Le risorse non possono essere recuperate tramite cicli a guadagno netto.
7. Ogni eccezione deve indicare esplicitamente la regola che modifica.

## Regole canoniche

Le regole MR-RULE-001 - MR-RULE-014 sono definite in `data/canonical_rules.yml`. Ogni modifica richiede un ADR in `docs/decisions`, aggiornamento dei test e nuova versione del prodotto.

## Gerarchia delle fonti

1. `data/canonical_rules.yml`
2. capitolo 5, Come si gioca
3. capitolo 6, Mosse base
4. capitoli dei poteri
5. quick reference
6. FAQ

La gerarchia serve soltanto per diagnosticare una regressione. Una release candidata non deve contenere divergenze tra questi livelli.
