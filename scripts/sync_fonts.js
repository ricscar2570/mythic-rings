/**
 * Materializza i font web dalle dipendenze @fontsource.
 * I file binari non sono conservati nel pacchetto sorgente: `npm ci` li
 * installa secondo package-lock.json e questo script prepara assets/fonts/.
 */
'use strict';
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const target = path.join(root, 'assets', 'fonts');
const files = {
  'EBGaramond-Regular.woff2': '@fontsource/eb-garamond/files/eb-garamond-latin-400-normal.woff2',
  'EBGaramond-Italic.woff2': '@fontsource/eb-garamond/files/eb-garamond-latin-400-italic.woff2',
  'EBGaramond-Bold.woff2': '@fontsource/eb-garamond/files/eb-garamond-latin-700-normal.woff2',
  'EBGaramond-BoldItalic.woff2': '@fontsource/eb-garamond/files/eb-garamond-latin-700-italic.woff2',
  'Cinzel-Regular.woff2': '@fontsource/cinzel/files/cinzel-latin-400-normal.woff2',
  'Cinzel-Bold.woff2': '@fontsource/cinzel/files/cinzel-latin-700-normal.woff2',
  'CinzelDecorative.woff2': '@fontsource/cinzel-decorative/files/cinzel-decorative-latin-700-normal.woff2',
};

fs.mkdirSync(target, { recursive: true });
for (const [name, modulePath] of Object.entries(files)) {
  let source;
  try {
    source = require.resolve(modulePath, { paths: [root] });
  } catch (error) {
    console.error(`Dipendenza font non trovata: ${modulePath}`);
    process.exitCode = 1;
    continue;
  }
  fs.copyFileSync(source, path.join(target, name));
}
if (!process.exitCode) {
  console.log(`Font web materializzati in ${path.relative(root, target)}/`);
}
