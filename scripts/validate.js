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

  // ---- INVARIANTI DI CONTENUTO v3.2 (anti-regressione) ----
  const C = fm.content;
  const lines = C.split('\n');

  // Tabelle: corruzione da reflow a larghezza fissa (spazi multipli dentro le celle)
  lines.forEach((line, i) => {
    if (/^\s*\|/.test(line) && /\|[^|]*\S {3,}\S[^|]*\|/.test(line)) {
      err(name, `Riga ${i+1}: tabella corrotta (cella con spazi multipli interni)`);
    }
  });

  // Tabelle: coerenza numero di pipe (header vs righe dati)
  {
    let hdr = null, inT = false;
    for (let i = 0; i < lines.length; i++) {
      const s = lines[i].trim();
      if (/^\|?[\s:]*-{2,}.*\|/.test(s) && (s.match(/\|/g) || []).length >= 2) {
        for (let j = i - 1; j >= 0; j--) {
          const p = lines[j].trim();
          if (p.startsWith('|')) { hdr = (p.match(/\|/g) || []).length; break; }
          if (p === '') continue; else { hdr = null; break; }
        }
        inT = true; continue;
      }
      if (inT) {
        if (s.startsWith('|')) {
          const c = (s.match(/\|/g) || []).length;
          if (hdr && c !== hdr) err(name, `Riga ${i + 1}: colonne tabella incoerenti (${c} pipe vs ${hdr})`);
        } else { inT = false; hdr = null; }
      }
    }
  }

  // Mictlan PF: formula v3.1 vietata fuori dalla FAQ (che la cita come storia)
  if (!/faq/i.test(name) && /24\s*\+\s*\(?\s*FOR\s*[×x]\s*2/i.test(C)) {
    err(name, `Formula PF Mictlan obsoleta "24+(FOR×2)" — canonico v3.2: 28+(FOR×1)`);
  }

  // Stress 10 / Corruzione: modello "bloccato" vietato (v3.2 = poteri "sospesi")
  if (/incapace di agire per 24/i.test(C) || /poteri a pagamento sono BLOCCATI/i.test(C)) {
    err(name, `Modello Stress/Corruzione obsoleto (bloccato) — v3.2 usa "sospesi"`);
  }

  // Escalation Die: avvio al round 4 vietato (v3.2 parte dal round 3)
  if (/round 4 in poi/i.test(C)) {
    err(name, `Escalation Die obsoleto ("round 4 in poi") — v3.2 parte dal round 3`);
  }

  // Corruzione: scala 0-10 obsoleta (v3.2 = 0-8)
  if (/Corruzione\s*\(scala\s*0-10\)/i.test(C) || /Corruzione[^.]{0,40}\b0 a 10\b/i.test(C)) {
    err(name, `Scala Corruzione obsoleta "0-10" — v3.2 = 0-8`);
  }

  // Versione prodotto
  if (fm.data.version && String(fm.data.version) !== '3.2') {
    warn(name, `version: ${fm.data.version} (atteso 3.2)`);
  }

  // ---- GUARDRAIL ANTI-REGRESSIONE (sessione fix layout v3.2) ----

  // G1. Em dash vietati (Step 1): nessun "—" nei capitoli
  {
    let n = 0;
    lines.forEach((line, i) => {
      if (line.includes('\u2014')) { err(name, `Riga ${i + 1}: em dash "—" vietato (usare ":", "," o "-")`); n++; }
    });
  }

  // G2. Righe vuote attorno alle tabelle (Step 3): senza, il motore perde il testo
  //     dopo la tabella. Ogni blocco tabella GFM deve avere riga vuota prima e dopo.
  {
    const isT = (l) => { const s = l.trim(); return s.startsWith('|') && s.endsWith('|'); };
    const isSep = (l) => /^\|[\s:|-]+\|$/.test(l.trim());
    let i = 0;
    while (i < lines.length) {
      if (isT(lines[i])) {
        const start = i;
        while (i < lines.length && isT(lines[i])) i++;
        const end = i - 1;
        const hasSep = lines.slice(start, end + 1).some(isSep);
        if (hasSep) {
          if (start > 0 && lines[start - 1].trim() !== '')
            err(name, `Riga ${start + 1}: tabella senza riga vuota PRIMA (il testo precedente puo' fondersi)`);
          if (end + 1 < lines.length && lines[end + 1].trim() !== '')
            err(name, `Riga ${end + 2}: tabella senza riga vuota DOPO (il testo successivo va perso)`);
        }
      } else i++;
    }
  }

  // G3. Corsivo non chiuso (Step 3): paragrafo che apre con "*" singolo e resta dispari
  {
    const countSingle = (t) => t.replace(/\\\*/g, '').replace(/\*\*/g, '').split('*').length - 1;
    const boundary = (l) => { const s = l.trim(); return s === '' || s.startsWith(':::') || s.startsWith('|') || s.startsWith('#'); };
    let i = 0;
    while (i < lines.length) {
      if (boundary(lines[i])) { i++; continue; }
      const s = i;
      while (i < lines.length && !boundary(lines[i])) i++;
      const para = lines.slice(s, i);
      const first = para[0].replace(/^\s+/, '');
      if (first.startsWith('*') && !first.startsWith('**') && countSingle(para.join('\n')) % 2 === 1) {
        warn(name, `Riga ${s + 1}: corsivo non chiuso ("*" dispari) — l'asterisco appare letterale`);
      }
    }
  }

  // G4. Titolo box con asterischi (Step 3): vengono resi letteralmente
  {
    const bt = fm.content.matchAll(/:::box\[([^\]]*)\]/g);
    for (const m of bt) {
      if (m[1].includes('*')) warn(name, `Titolo box con "*": "${m[1].trim()}" (l'asterisco appare letterale)`);
    }
  }

  // G5. Coerenza struttura in 7 parti (Step 5): part deve corrispondere al capitolo
  {
    const ch = Number(fm.data.chapter);
    const expected = ch <= 4 ? 'Parte I' : ch <= 6 ? 'Parte II' : ch <= 10 ? 'Parte III'
                   : ch <= 14 ? 'Parte IV' : ch <= 25 ? 'Parte V' : ch <= 28 ? 'Parte VI' : 'Parte VII';
    const p = String(fm.data.part || '');
    if (ch && p && !p.startsWith(expected + ':') && p !== expected) {
      err(name, `part "${p}" incoerente: cap ${ch} dovrebbe essere "${expected}: ..."`);
    }
  }

  // G6. Divisori versione nel corpo: "MYTHIC RINGS vX" deve essere v3.2
  {
    const vm = C.matchAll(/MYTHIC RINGS\s+v(\d+\.\d+)/g);
    for (const m of vm) {
      if (m[1] !== '3.2') err(name, `Divisore versione datato: "MYTHIC RINGS v${m[1]}" (atteso v3.2)`);
    }
  }

  if (errors === 0 || true) ok(name, `OK (${words} parole)`);
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
