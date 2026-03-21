/**
 * MYTHIC RINGS v3 — Validator
 * Verifica che ogni capitolo abbia frontmatter corretto
 * e che la sintassi custom sia ben formata.
 */

'use strict';

const fs   = require('fs');
const path = require('path');
const glob = require('glob');
const matter = require('gray-matter');
const chalk  = require('chalk');

const REQUIRED_FIELDS = ['title', 'chapter', 'part'];
const VALID_BOX_TYPES = [
  'warn','info','tip','danger','example','rule',
  'casata_avalon','casata_umbra','casata_ife','casata_mictlan',
];

let errors = 0;
let warnings = 0;

function err(file, msg)  { console.error(chalk.red(`  ✗  ${file}: ${msg}`));   errors++; }
function warn(file, msg) { console.warn(chalk.yellow(`  ⚠  ${file}: ${msg}`)); warnings++; }
function ok(file, msg)   { console.log(chalk.green(`  ✓  ${file}: ${msg}`)); }

const dir = process.argv[2] || './chapters';
const files = glob.sync(`${dir}/*.md`).sort();

if (!files.length) {
  console.error(chalk.red(`Nessun file .md trovato in: ${dir}`));
  process.exit(1);
}

console.log(chalk.bold.cyan(`\n📋 Validazione ${files.length} capitoli...\n`));

for (const f of files) {
  const name = path.basename(f);
  const raw  = fs.readFileSync(f, 'utf8');

  let fm;
  try {
    fm = matter(raw);
  } catch(e) {
    err(name, `Frontmatter non valido: ${e.message}`);
    continue;
  }

  // Campi obbligatori
  for (const field of REQUIRED_FIELDS) {
    if (!fm.data[field]) warn(name, `Campo mancante: "${field}"`);
  }

  // Numerazione capitolo
  if (fm.data.chapter && isNaN(Number(fm.data.chapter))) {
    err(name, `"chapter" deve essere un numero, trovato: "${fm.data.chapter}"`);
  }

  // Verifica box types
  const boxMatches = fm.content.matchAll(/:::box\[[^\]]*\]\{type=([^}]+)\}/g);
  for (const m of boxMatches) {
    const type = m[1];
    if (!VALID_BOX_TYPES.includes(type)) {
      warn(name, `Tipo box sconosciuto: "${type}". Validi: ${VALID_BOX_TYPES.join(', ')}`);
    }
  }

  // Verifica container bilanciati
  const opens  = (fm.content.match(/^:::/gm) || []).length;
  if (opens % 2 !== 0) {
    warn(name, `Numero dispari di ":::" — container non chiusi? (${opens} totali)`);
  }

  // Verifica lunghezza ragionevole
  const words = fm.content.split(/\s+/).length;
  if (words < 100) warn(name, `Capitolo molto breve: ${words} parole`);
  if (words > 8000) warn(name, `Capitolo molto lungo: ${words} parole — considera di dividerlo`);

  ok(name, `OK (${words} parole)`);
}

console.log('');
if (errors > 0) {
  console.error(chalk.bold.red(`\n  ✗  ${errors} errori, ${warnings} avvisi\n`));
  process.exit(1);
} else if (warnings > 0) {
  console.warn(chalk.bold.yellow(`\n  ⚠  0 errori, ${warnings} avvisi — build possibile\n`));
} else {
  console.log(chalk.bold.green(`\n  ✅  Tutti i capitoli validi (${files.length} file)\n`));
}
