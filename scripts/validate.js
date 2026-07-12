#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const yaml = require('js-yaml');
const chalk = require('chalk');
const { loadMeta } = require('../build/project-meta');

const root = path.resolve(__dirname, '..');
const meta = loadMeta(root);
const allowedStatus = new Set(['bozza', 'revisione', 'beta', 'rc', 'finale']);
const required = ['title', 'chapter', 'part', 'status', 'version'];
const validBoxTypes = new Set(['warn','info','tip','danger','example','rule','casata_avalon','casata_umbra','casata_ife','casata_mictlan']);
const forbidden = [
  [/Riccardo\s*\[Cognome\]/i, 'placeholder autore'],
  [/\[Nome playtester\]/i, 'placeholder playtester'],
  [/ISBN:\s*0{3}/i, 'ISBN fittizio'],
  [/Aggiornamenti?\s+v?\d/i, 'nota di aggiornamento nel manuale'],
  [/Tracker Modifiche/i, 'tracker interno nel manuale'],
  [/Rationale\s*(?:design)?\s*:/i, 'rationale di sviluppo nel manuale'],
  [/\bM(?:10|13|14|15|16|17|18|19|20|21|24)\b/, 'identificatore interno di modifica'],
  [/nella\s+v\d/i, 'confronto con versione precedente'],
  [/versione\s+(?:originale|precedente)/i, 'confronto con versione precedente'],
  [/ritira\s+(?:TUTTI|entrambi)\s+i?\s*dadi/i, 'Punti Fato obsoleti: rilancio di entrambi i dadi'],
  [/inizi\s+ogni\s+sessione\s+con\s+1/i, 'Punti Fato obsoleti: 1 iniziale'],
  [/massimo\s+3[^.\n]*Punti?\s+Fato/i, 'Punti Fato obsoleti: massimo 3'],
  [/turno\s+frenetico/i, 'Punti Fato obsoleti: azione aggiuntiva'],
  [/guadagnar(?:e|i)\s+Punti?\s+Fato/i, 'Punti Fato obsoleti: guadagno libero'],
  [/Escalation[^\n]{0,120}\+\d\s+(?:al\s+)?tiro/i, 'Escalation obsoleta: bonus al tiro'],
  [/Armatura[^\n]{0,60}(?:5\+|da\s+0\s+a\s+5)/i, 'Armatura oltre il limite canonico'],
];

let errors = 0;
let warnings = 0;
const report = { version: meta.version, files: [], errors: [], warnings: [] };
function issue(kind, file, message, line = null) {
  const item = { file, message, ...(line ? { line } : {}) };
  report[kind === 'error' ? 'errors' : 'warnings'].push(item);
  if (kind === 'error') errors++; else warnings++;
  const label = kind === 'error' ? chalk.red('ERRORE') : chalk.yellow('AVVISO');
  console.log(`  ${label} ${file}${line ? ':' + line : ''} - ${message}`);
}

function pipeCount(s) { return (s.match(/\|/g) || []).length; }
function validateTables(lines, file) {
  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i].trim();
    const sep = lines[i + 1].trim();
    if (!line.startsWith('|') || !/^\|?\s*:?-{3,}/.test(sep)) continue;
    const expected = pipeCount(line);
    let j = i + 2;
    while (j < lines.length && lines[j].trim().startsWith('|')) {
      if (pipeCount(lines[j]) !== expected) issue('error', file, `tabella con ${pipeCount(lines[j])} pipe; attese ${expected}`, j + 1);
      j++;
    }
  }
}

function chapterExpectedPart(ch) {
  if (ch <= 4) return 'Parte I:';
  if (ch <= 6) return 'Parte II:';
  if (ch <= 10) return 'Parte III:';
  if (ch <= 14) return 'Parte IV:';
  if (ch <= 25) return 'Parte V:';
  if (ch <= 28) return 'Parte VI:';
  return 'Parte VII:';
}

console.log(chalk.bold.cyan(`\nMythic Rings ${meta.version} - validazione editoriale e tecnica\n`));
const manifest = meta.chapters.map(p => path.normalize(p));
const seenChapters = new Map();
const seenTitles = new Map();

for (let index = 0; index < manifest.length; index++) {
  const rel = manifest[index];
  const abs = path.join(root, rel);
  const file = path.basename(rel);
  if (!fs.existsSync(abs)) { issue('error', file, 'file dichiarato nel manifest ma assente'); continue; }
  const raw = fs.readFileSync(abs, 'utf8');
  let parsed;
  try { parsed = matter(raw); } catch (e) { issue('error', file, `frontmatter non valido: ${e.message}`); continue; }
  const fm = parsed.data;
  for (const field of required) if (fm[field] === undefined || fm[field] === null || fm[field] === '') issue('error', file, `campo obbligatorio mancante: ${field}`);
  const ch = Number(fm.chapter);
  if (!Number.isInteger(ch)) issue('error', file, 'chapter deve essere un intero');
  else {
    if (ch !== index + 1) issue('error', file, `ordine manifest ${index + 1}, frontmatter ${ch}`);
    if (seenChapters.has(ch)) issue('error', file, `numero capitolo duplicato con ${seenChapters.get(ch)}`);
    seenChapters.set(ch, file);
    if (!String(fm.part || '').startsWith(chapterExpectedPart(ch))) issue('error', file, `parte incoerente per il capitolo ${ch}`);
  }
  if (seenTitles.has(fm.title)) issue('error', file, `titolo duplicato con ${seenTitles.get(fm.title)}`); else seenTitles.set(fm.title, file);
  if (!allowedStatus.has(String(fm.status))) issue('error', file, `status non ammesso: ${fm.status}`);
  if (String(fm.version) !== String(meta.version)) issue('error', file, `version ${fm.version}; attesa ${meta.version}`);

  const lines = parsed.content.split('\n');
  validateTables(lines, file);
  const markers = (parsed.content.match(/^:::/gm) || []).length;
  if (markers % 2 !== 0) issue('error', file, `container ::: non bilanciati (${markers})`);
  for (const m of parsed.content.matchAll(/:::box\[[^\]]*\]\{type=([^}]+)\}/g)) {
    if (!validBoxTypes.has(m[1])) issue('error', file, `tipo box non valido: ${m[1]}`);
  }
  for (const [rx, description] of forbidden) {
    const m = rx.exec(parsed.content);
    if (m) {
      const line = parsed.content.slice(0, m.index).split('\n').length;
      issue('error', file, description, line);
    }
  }
  if (/\|\s*PF\s*\|\s*Armatura\s*\|\s*Attacco\s*\|/i.test(parsed.content)) issue('error', file, 'stat block con colonna Attacco: il Custode non tira');
  const words = parsed.content.trim().split(/\s+/).filter(Boolean).length;
  if (words < 180) issue('warning', file, `capitolo molto breve: ${words} parole`);
  if (words > 8000) issue('warning', file, `capitolo molto lungo: ${words} parole`);
  report.files.push({ file, chapter: ch, words, status: fm.status });
}

const actual = fs.readdirSync(path.join(root, 'chapters')).filter(f => f.endsWith('.md')).map(f => path.normalize('chapters/' + f)).sort();
for (const f of actual) if (!manifest.includes(f)) issue('error', path.basename(f), 'capitolo presente ma non dichiarato nel manifest');

const canonical = yaml.load(fs.readFileSync(path.join(root, 'data/canonical_rules.yml'), 'utf8'));
if (String(canonical.product_version) !== String(meta.version)) issue('error', 'data/canonical_rules.yml', 'versione canonica diversa da book.yml');
const ids = new Set();
for (const [key, rule] of Object.entries(canonical.rules || {})) {
  if (!rule.id || !/^MR-RULE-\d{3}$/.test(rule.id)) issue('error', 'data/canonical_rules.yml', `id non valido per ${key}`);
  if (ids.has(rule.id)) issue('error', 'data/canonical_rules.yml', `id duplicato ${rule.id}`);
  ids.add(rule.id);
}

fs.mkdirSync(path.join(root, 'dist'), { recursive: true });
fs.writeFileSync(path.join(root, 'dist', 'validation-report.json'), JSON.stringify(report, null, 2));
console.log('');
if (errors) {
  console.log(chalk.bold.red(`${errors} errori, ${warnings} avvisi. Build bloccata.\n`));
  process.exit(1);
}
console.log(warnings ? chalk.bold.yellow(`0 errori, ${warnings} avvisi.\n`) : chalk.bold.green('Validazione superata senza errori.\n'));
