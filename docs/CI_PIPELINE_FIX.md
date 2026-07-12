# Correzione della pipeline CI

## Problema osservato

Il workflow eseguiva `npm run release:check` dopo un checkout pulito. Il comando verificava i sorgenti e lanciava direttamente il preflight su `dist/`, ma `dist/` è esclusa da Git tramite `.gitignore`. Di conseguenza il preflight segnalava come assenti tutti i tredici artefatti editoriali.

## Semantica corretta dei comandi

- `npm run verify`: controlla esclusivamente sorgenti, regole canoniche e dati strutturati.
- `npm run release:preflight`: ricontrolla i sorgenti e valida artefatti già presenti in `dist/`.
- `npm run release:check`: pulisce `dist/`, ricostruisce manuale e prodotti, quindi esegue il preflight. È il gate da usare in CI e prima di una release.
- `npm run release:build`: alias esplicito di `release:check`.

## Robustezza di LibreOffice

Sui runner Linux LibreOffice può completare la scrittura del PDF e lasciare comunque vivo il processo headless. La conversione dei prodotti ora:

1. osserva il file PDF atteso;
2. richiede che la dimensione rimanga stabile;
3. apre il PDF con PyMuPDF;
4. forza il caricamento dell'ultima pagina;
5. termina in modo controllato l'eventuale processo LibreOffice rimasto sospeso;
6. rifiuta file vuoti, parziali o illeggibili.

## Verifica eseguita

Comando lanciato con `dist/` assente:

```bash
rm -rf dist
npm run release:check
```

Risultato:

- exit code: `0`;
- durata nell'ambiente di verifica: `38,19 s`;
- 33 capitoli validati;
- 61 poteri e 31 avversari sottoposti ad audit;
- 13 artefatti trovati e verificati;
- manuale: 387 pagine, 36 segnalibri;
- quickstart: 22 pagine, 14 segnalibri;
- kit del giocatore: 10 pagine, 9 segnalibri;
- avventura: 11 pagine, 8 segnalibri;
- `npm audit`: 0 vulnerabilità note.

Rimane un solo avviso editoriale non bloccante: il capitolo sui dodici quartieri contiene 8.577 parole.
