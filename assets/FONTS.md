# Font web

I file WOFF2 usati dalla pipeline non sono conservati nel pacchetto sorgente.
Dopo `npm ci`, lo script `scripts/sync_fonts.js` li materializza in
`assets/fonts/` a partire dalle dipendenze `@fontsource` bloccate in
`package-lock.json`.
