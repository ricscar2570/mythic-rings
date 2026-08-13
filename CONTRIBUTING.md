# Contribuire a Mythic Rings

## Principio fondamentale

Ogni modifica deve preservare una sola fonte di verità. Le regole non vengono corrette isolatamente in FAQ, quick reference o avventure.

## Flusso di lavoro

1. Creare un branch dal ramo di sviluppo.
2. Associare la modifica a un ID stabile presente in `docs/project/ISSUE_REGISTER.csv`; usare `roadmap_ref` soltanto come riferimento al piano.
3. Per una scelta meccanica significativa, aggiungere o aggiornare un ADR in `docs/decisions/`.
4. Aggiornare `data/canonical_rules.yml` e `docs/CANONICAL_RULES_SPEC.md`.
5. Verificare terminologia e grafie contro `docs/EDITORIAL_STYLE_GUIDE.md`.
6. Aggiornare capitoli, esempi e prodotti derivati.
7. Se si modifica il bestiario, intervenire in `data/adversaries.yml` e rigenerare il capitolo.
8. Eseguire `npm run verify`.
9. In beta e in CI, eseguire `npm run release:check`: il comando ricostruisce `dist/`, rigenera la paginazione e poi esegue il preflight. Prima di una RC/1.0, eseguire un refresh, committare `data/toc-pages.lock.json` e verificare un checkout pulito con `npm run release:locked`. Usare `npm run release:preflight` soltanto per controllare artefatti già presenti.
10. Aggiornare `CHANGELOG.md` e, quando la modifica cambia canon/regole/bilanciamento/testo/layout, `docs/project/CHANGELOG_MASTER.csv`.
11. Non modificare mai in-place una baseline sotto `archive/baselines/`; una nuova baseline richiede una nuova directory/versione.

## Definition of Done

Una modifica è completata quando:

- non introduce una seconda formulazione della stessa regola;
- comprende esempi o casi limite quando necessari;
- supera validator, test canonici e audit semantico;
- aggiorna quickstart, FAQ e riferimenti rapidi se coinvolti;
- registra gli effetti sul playtest e, se produce dati comparabili, usa il modello in `docs/playtest/`;
- non contiene placeholder o dati personali non autorizzati;
- non modifica file generati senza aggiornare la fonte strutturata;
- rispetta `docs/EDITORIAL_STYLE_GUIDE.md`, in particolare **Custode = GM**, **Guardiano = singolo portatore** e le distanze **Contatto/Vicino/Lontano/Remoto**.

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

## Modifiche al canon di mondo

Dopo G1, `data/canon/` è la fonte strutturata del mondo. Una modifica a Linee, Nexus, roster, cronologia, numeri o istituzioni deve:

1. citare una issue/decisione stabile;
2. aggiornare prima il file YAML proprietario;
3. aggiornare le viste `docs/CANON_*` e i capitoli interessati;
4. aggiornare le note di ricerca se entra in gioco un fatto reale;
5. eseguire `npm run phase1:check`.

Non reintrodurre bonus numerici locali per Linee/Nexus senza una change request che riapra DEC-004. Non usare PNG canonici come pregenerati senza decisione esplicita.
