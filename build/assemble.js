/**
 * MYTHIC RINGS v3 — Assembler
 * Converte il DOCX in PDF tramite LibreOffice headless
 * e lo copia nella cartella dist/
 */

'use strict';

const { execSync, spawnSync } = require('child_process');
const path = require('path');
const fs   = require('fs');
const glob = require('glob');

const DIST_DIR = path.resolve(process.argv[2] || './dist');
const PDF_DIR  = path.join(DIST_DIR, 'pdf');

function log(msg)  { console.log('\x1b[36m' + msg + '\x1b[0m'); }
function ok(msg)   { console.log('\x1b[32m  ✅  ' + msg + '\x1b[0m'); }
function err(msg)  { console.error('\x1b[31m  ✗  ' + msg + '\x1b[0m'); }

function findLibreOffice() {
  const candidates = [
    'libreoffice', 'soffice',
    '/usr/bin/libreoffice', '/usr/bin/soffice',
    '/Applications/LibreOffice.app/Contents/MacOS/soffice',
    'C:\\Program Files\\LibreOffice\\program\\soffice.exe',
  ];
  for (const c of candidates) {
    try {
      execSync(`"${c}" --version`, { stdio: 'ignore' });
      return c;
    } catch {}
  }
  return null;
}

function buildPDF() {
  log('\n📄 MYTHIC RINGS v3 — PDF Builder\n');

  const docxFiles = glob.sync(`${DIST_DIR}/*.docx`);
  if (!docxFiles.length) {
    err(`Nessun DOCX trovato in ${DIST_DIR}. Esegui prima: npm run build`);
    process.exit(1);
  }

  const lo = findLibreOffice();
  if (!lo) {
    err('LibreOffice non trovato. Installalo con: sudo apt-get install libreoffice');
    err('macOS: brew install --cask libreoffice');
    process.exit(1);
  }
  log(`LibreOffice: ${lo}`);

  if (!fs.existsSync(PDF_DIR)) fs.mkdirSync(PDF_DIR, { recursive: true });

  for (const docx of docxFiles) {
    const basename = path.basename(docx, '.docx');
    log(`  Conversione: ${path.basename(docx)}`);

    const result = spawnSync(lo, [
      '--headless',
      '--convert-to', 'pdf',
      '--outdir', PDF_DIR,
      docx,
    ], { stdio: 'pipe', timeout: 120_000 });

    if (result.status !== 0) {
      err(`Conversione fallita: ${result.stderr?.toString()}`);
      process.exit(1);
    }

    const pdfPath = path.join(PDF_DIR, basename + '.pdf');
    if (fs.existsSync(pdfPath)) {
      const kb = Math.round(fs.statSync(pdfPath).size / 1024);
      ok(`${basename}.pdf  (${kb} KB)`);
    }
  }

  // Lista PDF generati
  const pdfs = glob.sync(`${PDF_DIR}/*.pdf`);
  console.log(`\n  PDF generati: ${pdfs.length}`);
  pdfs.forEach(p => console.log(`    ${path.basename(p)}`));
  console.log('');
}

buildPDF();
