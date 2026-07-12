/**
 * Mythic Rings - build PDF ufficiale a due passaggi.
 * 1. converte il DOCX preliminare;
 * 2. estrae i numeri di pagina dei capitoli;
 * 3. rigenera il DOCX con indice paginato;
 * 4. converte e post-processa il PDF definitivo.
 */
'use strict';
const { execFileSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const { loadMeta } = require('./project-meta');
const PROJECT = loadMeta(__dirname);

const distDir = path.resolve(process.argv[2] || './dist');
const docxPath = path.join(distDir, `${PROJECT.output_basename}.docx`);
const pdfPath = path.join(distDir, `${PROJECT.output_basename}.pdf`);
const tocPath = path.join(distDir, 'toc-pages.json');

function findLibreOffice() {
  const candidates = ['libreoffice', 'soffice', '/usr/bin/libreoffice', '/usr/bin/soffice', '/Applications/LibreOffice.app/Contents/MacOS/soffice', 'C:\\Program Files\\LibreOffice\\program\\soffice.exe'];
  for (const c of candidates) {
    try { execFileSync(c, ['--version'], { stdio: 'ignore' }); return c; } catch (_) {}
  }
  return null;
}

function fail(result, label) {
  console.error(result.stderr || result.stdout || label);
  process.exit(1);
}

function convert(lo, profileName) {
  const profile = path.join(distDir, profileName);
  fs.mkdirSync(profile, { recursive: true });
  if (fs.existsSync(pdfPath)) fs.unlinkSync(pdfPath);
  const result = spawnSync(lo, [
    `-env:UserInstallation=file://${profile.replace(/\\/g, '/')}`,
    '--headless', '--convert-to', 'pdf', '--outdir', distDir, docxPath,
  ], { encoding: 'utf8', timeout: 300000 });
  if (result.status !== 0) fail(result, 'Conversione PDF fallita.');
  if (!fs.existsSync(pdfPath)) {
    console.error(`LibreOffice non ha prodotto il file atteso: ${pdfPath}`);
    process.exit(1);
  }
}

if (!fs.existsSync(docxPath)) {
  console.error(`DOCX non trovato: ${docxPath}. Esegui npm run build:docx.`);
  process.exit(1);
}
const lo = findLibreOffice();
if (!lo) {
  console.error('LibreOffice non trovato: necessario per la build PDF ufficiale.');
  process.exit(1);
}
fs.mkdirSync(distDir, { recursive: true });
console.log(`\nBuild ${PROJECT.title} ${PROJECT.version} - PDF a due passaggi\n`);

// Passaggio 1: PDF preliminare per individuare le pagine reali.
convert(lo, '.lo-profile-pass1');
const extract = spawnSync('python3', [path.join(__dirname, 'extract_toc_pages.py'), pdfPath, tocPath], { encoding: 'utf8', timeout: 120000 });
if (extract.status !== 0) fail(extract, 'Estrazione indice fallita.');
process.stdout.write(extract.stdout || '');

// Rigenera il DOCX con l'indice paginato.
const rebuild = spawnSync(process.execPath, [path.join(__dirname, 'engine.js'), path.join(PROJECT.root, 'chapters'), distDir], {
  cwd: PROJECT.root,
  encoding: 'utf8',
  timeout: 300000,
  env: { ...process.env, MYTHIC_TOC_PAGES: tocPath },
});
if (rebuild.status !== 0) fail(rebuild, 'Rigenerazione DOCX con indice fallita.');
process.stdout.write(rebuild.stdout || '');

// Passaggio 2: PDF finale.
convert(lo, '.lo-profile-pass2');
const post = spawnSync('python3', [path.join(__dirname, 'postprocess_pdf.py'), pdfPath], { encoding: 'utf8', timeout: 120000 });
if (post.status !== 0) fail(post, 'Post-processing PDF fallito.');
process.stdout.write(post.stdout || '');
console.log(`PDF generato: ${pdfPath} (${Math.round(fs.statSync(pdfPath).size / 1024)} KB)\n`);
