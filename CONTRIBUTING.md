# Contribuire a Mythic Rings

## Principio fondamentale

Ogni modifica deve preservare una sola fonte di verità. Le regole non vengono corrette isolatamente in FAQ, quick reference o avventure.

## Flusso di lavoro

1. Creare un branch dal ramo di sviluppo.
2. Associare la modifica a un'issue.
3. Per una scelta meccanica significativa, aggiungere o aggiornare un ADR in `docs/decisions/`.
4. Aggiornare `data/canonical_rules.yml` e `docs/CANONICAL_RULES_SPEC.md`.
5. Aggiornare capitoli, esempi e prodotti derivati.
6. Se si modifica il bestiario, intervenire in `data/adversaries.yml` e rigenerare il capitolo.
7. Eseguire `npm run verify`.
8. Per una release candidate o in CI, eseguire `npm run release:check`: il comando ricostruisce `dist/` da zero e poi esegue il preflight. Usare `npm run release:preflight` soltanto per controllare artefatti già presenti.
9. Aggiornare `CHANGELOG.md`.

## Definition of Done

Una modifica è completata quando:

- non introduce una seconda formulazione della stessa regola;
- comprende esempi o casi limite quando necessari;
- supera validator, test canonici e audit semantico;
- aggiorna quickstart, FAQ e riferimenti rapidi se coinvolti;
- registra gli effetti sul playtest;
- non contiene placeholder o dati personali non autorizzati;
- non modifica file generati senza aggiornare la fonte strutturata.

## Commit

Usare messaggi chiari, per esempio:

```text
rules: canonizza il recupero fuori dal combattimento
bestiary: corregge le mosse del Basilisco
editorial: elimina duplicazione nel capitolo delle Casate
build: aggiunge il preflight dei prodotti derivati
```

## Pull request

La descrizione deve indicare:

- problema risolto;
- decisione adottata;
- file coinvolti;
- test eseguiti;
- impatto sul bilanciamento;
- necessità di playtest;
- eventuali diritti o fonti da verificare.

## Cose da non fare

- aggiungere nuove regole durante la correzione di un refuso;
- cambiare valori meccanici senza ADR e test;
- inserire una statistica Attacco nei PNG;
- introdurre azioni extra o bonus oltre i limiti canonici;
- usare nomi di collaboratori senza autorizzazione;
- dichiarare una release 1.0 prima del superamento dei gate esterni.
