/**
 * MYTHIC RINGS — HTML Renderer
 * Converte i capitoli .md in un documento HTML completo
 * per consultazione, debug e controllo di parità editoriale
 */
'use strict';

const fs   = require('fs');
const path = require('path');
const glob = require('glob');
const { parseFrontmatter, parse, NODE } = require('./md-parser');
const { loadMeta } = require('./project-meta');
const PROJECT = loadMeta(__dirname);

// ── Escape HTML ──────────────────────────────────────────────
function esc(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Render inline runs ───────────────────────────────────────
function renderRuns(runs) {
  if (!runs || !runs.length) return '';
  return runs.map(r => {
    let t = esc(r.text);
    if (r.code)   t = `<code>${t}</code>`;
    if (r.bold)   t = `<strong>${t}</strong>`;
    if (r.italic) t = `<em>${t}</em>`;
    return t;
  }).join('');
}

// ── Box type → CSS class ─────────────────────────────────────
const BOX_ICONS = {
  warn:           '⚠️',
  info:           '💡',
  tip:            '✅',
  danger:         '🔴',
  example:        '📖',
  rule:           '📏',
  casata_avalon:  '☀️',
  casata_umbra:   '🌑',
  casata_ife:     '🌿',
  casata_mictlan: '💀',
};

// ── Render nodo ──────────────────────────────────────────────
function renderNode(node, opts = {}) {
  const { inStatBlock = false, inBox = false } = opts;

  switch (node.type) {

    case NODE.HEADING: {
      const lvl = Math.min(Math.max(node.level, 1), 4);
      const txt = renderRuns(node.runs);
      // h1 dentro un capitolo usa column-span per uscire dalle colonne
      const cls = lvl === 1 ? ' class="section-heading"' : '';
      return `<h${lvl}${cls}>${txt}</h${lvl}>\n`;
    }

    case NODE.PARAGRAPH: {
      const txt = renderRuns(node.runs);
      if (!txt.trim()) return '';
      return `<p>${txt}</p>\n`;
    }

    case NODE.HR:
      return `<hr>\n`;

    case NODE.PAGEBREAK:
      return `<div class="page-break"></div>\n`;

    case NODE.COLBREAK:
      return `<div class="col-break"></div>\n`;

    case NODE.LIST: {
      const tag = node.ordered ? 'ol' : 'ul';
      const items = (node.items || [])
        .map(item => `<li>${renderRuns(item.runs)}</li>`)
        .join('\n');
      return `<${tag}>\n${items}\n</${tag}>\n`;
    }

    case NODE.QUOTE: {
      const inner = (node.children || [])
        .map(c => renderNode(c, opts))
        .join('');
      return `<blockquote>${inner}</blockquote>\n`;
    }

    case NODE.BOX: {
      const btype = node.boxType || 'info';
      const cls   = `box box-${btype.replace(/_/g, '-')}`;
      const icon  = BOX_ICONS[btype] || '';
      const title = node.title
        ? `<span class="box-title">${icon ? icon + ' ' : ''}${esc(node.title)}</span>\n`
        : '';
      const inner = (node.children || [])
        .map(c => renderNode(c, { inBox: true }))
        .join('');
      return `<div class="${cls}">\n${title}${inner}</div>\n`;
    }

    case NODE.TABLE:
    case NODE.TABLE_WIDE: {
      const isWide = node.type === NODE.TABLE_WIDE;
      const cls    = isWide ? ' class="table-wide"' : '';
      const headers = node.headers || [];
      const rows    = node.rows    || [];

      let thead = '';
      if (headers.length) {
        const ths = headers.map(h => `<th>${renderRuns(h.runs)}</th>`).join('');
        thead = `<thead><tr>${ths}</tr></thead>\n`;
      }

      const tbody = rows.map(row => {
        const tds = row.map(cell => `<td>${renderRuns(cell.runs)}</td>`).join('');
        return `<tr>${tds}</tr>`;
      }).join('\n');

      return `<table${cls}>\n${thead}<tbody>\n${tbody}\n</tbody></table>\n`;
    }

    case NODE.STAT_BLOCK: {
      const inner = (node.children || [])
        .map(c => renderNode(c, { inStatBlock: true }))
        .join('');
      const name = esc(node.name || '');
      return `<div class="stat-block avoid-break">\n`
           + `<div class="stat-name">⚔️ ${name}</div>\n`
           + `${inner}</div>\n`;
    }

    default:
      return '';
  }
}

// ── Render un capitolo completo ──────────────────────────────
function renderChapter(ast, fm, chapterIndex) {
  const title    = esc(fm.title    || '');
  const part     = esc(fm.part     || '');
  const number   = fm.chapter      || '';
  const epigraph = fm.epigraph     || '';

  // Intestazione capitolo (column-span all, sfondo scuro)
  const header = `
<div class="chapter-header avoid-break">
  <span class="chapter-title-marker">${title}</span>
  ${part     ? `<div class="chapter-part-label">${part}</div>` : ''}
  ${number   ? `<div class="chapter-number">Capitolo ${number}</div>` : ''}
  <div class="chapter-title">${title}</div>
  ${epigraph ? `<div class="chapter-epigraph">«${esc(epigraph)}»</div>` : ''}
</div>
`;

  // Body: render tutti i nodi
  const body = (ast.nodes || []).map(n => renderNode(n)).join('');

  // Ogni capitolo inizia su nuova pagina (eccetto il primo)
  const pageBreak = chapterIndex > 0 ? '<div class="page-break"></div>\n' : '';

  return `${pageBreak}${header}\n<div class="chapter-body">\n${body}\n</div>\n`;
}

// ── Copertina HTML ───────────────────────────────────────────
function buildCover() {
  return `
<div class="cover-page">
  <div class="cover-eyebrow">${esc(PROJECT.system_description)}</div>
  <div class="cover-title">${esc(PROJECT.title).replace(/ /g, '<br>')}</div>
  <div class="cover-version">${esc(PROJECT.edition)}</div>
  <div class="cover-rule"></div>
  <div class="cover-subtitle">
    ${esc(PROJECT.subtitle)}<br>
    <br>
    ${esc(PROJECT.tagline)}
  </div>
  <div class="cover-tagline">Versione ${esc(PROJECT.version)}</div>
</div>
`;
}

// ── Back matter HTML ──────────────────────────────────────────
function buildBackMatter() {
  const contacts = [PROJECT.website, PROJECT.contact].filter(Boolean).map(esc).join(' · ');
  const isbn = PROJECT.isbn ? `<p>ISBN: ${esc(PROJECT.isbn)}</p>` : '';
  return `
<div class="page-break"></div>
<div class="chapter-header avoid-break">
  <div class="chapter-title">Colophon</div>
</div>
<div class="chapter-body">
  <h2>${esc(PROJECT.title)} - ${esc(PROJECT.subtitle)}</h2>
  <p><strong>${esc(PROJECT.edition)} - versione ${esc(PROJECT.version)} (${esc(String(PROJECT.copyright_year))})</strong></p>
  <p>Ideazione, testo e game design: ${esc(PROJECT.author)}.</p>
  <p>Sviluppo editoriale e manutenzione della presente edizione: ${esc(PROJECT.author)}.</p>
  <p>Mythic Rings e Guardiani di Milano sono opere di fantasia. Nomi, personaggi, luoghi ed eventi, per quanto ispirati alla città di Milano, sono usati in modo fittizio.</p>
  <p>Mythic Rings è un gioco ispirato ai principi Powered by the Apocalypse. La dicitura definitiva e ogni attribuzione aggiuntiva devono essere verificate prima della release commerciale.</p>
  <p>Copyright © ${esc(String(PROJECT.copyright_year))} ${esc(PROJECT.author)}. Tutti i diritti riservati.</p>
  ${isbn}
  ${contacts ? `<p>${contacts}</p>` : ''}
</div>
<div class="page-break"></div>
<div class="chapter-header avoid-break">
  <div class="chapter-title">Crediti e Ringraziamenti</div>
</div>
<div class="chapter-body">
  <h2>Autore</h2>
  <p>${esc(PROJECT.author)} - ideazione, testo e game design.</p>
  <h2>Stato dei crediti</h2>
  <p>Questa è una versione beta editoriale. I crediti nominativi di editing, consulenza e playtest saranno inseriti esclusivamente dopo conferma scritta e prima della release commerciale.</p>
  <h2>Ringraziamenti</h2>
  <p>Grazie ai lettori e ai tavoli che contribuiranno alla verifica della Prima Edizione.</p>
</div>`;
}

// ── Documento HTML completo ──────────────────────────────────
function buildFullHTML(chaptersDir, cssPath) {
  const files = PROJECT.chapters.map(rel => path.join(PROJECT.root, rel));
  if (!files.length) {
    console.error('Nessun capitolo trovato in ' + chaptersDir);
    process.exit(1);
  }

  // Carica il CSS come stringa inline (WeasyPrint non segue percorsi relativi
  // in modo affidabile da riga di comando)
  const cssAbs  = path.resolve(cssPath);
  const cssDir  = path.dirname(cssAbs);
  let   cssText = fs.readFileSync(cssAbs, 'utf8');

  // Sostituisci url('../assets/fonts/...') con percorsi assoluti
  cssText = cssText.replace(
    /url\(['"]?\.\.\//g,
    `url('${path.resolve(cssDir, '..')}${path.sep}`
      .replace(/\\/g, '/')  // Windows compat
  );
  // Chiudi la sostituzione del percorso
  cssText = cssText.replace(
    /url\('([^']*assets[^']*\.woff2)/g,
    (m, p) => `url('${p}`
  );

  // Build capitoli
  const chapters = files.map((f, idx) => {
    const raw  = fs.readFileSync(f, 'utf8');
    const { frontmatter: fm, content } = parseFrontmatter(raw);
    const ast  = parse(content, fm);
    process.stdout.write(`  ✓  ${path.basename(f).padEnd(44)} → ${(fm.title || '').substring(0, 30)}\n`);
    return renderChapter(ast, fm, idx);
  });

  // TOC semplice (i capitoli con titolo e numero)
  const tocEntries = files.map(f => {
    const raw = fs.readFileSync(f, 'utf8');
    const { frontmatter: fm } = parseFrontmatter(raw);
    if (!fm.title) return '';
    return `<div class="toc-entry">`
         + `${fm.chapter ? `<span>${fm.chapter}. </span>` : ''}`
         + `${esc(fm.title)}`
         + `<span class="toc-page-num"></span>`
         + `</div>`;
  }).join('\n');

  const toc = `
<div class="toc-page">
  <h1>Indice</h1>
  ${tocEntries}
</div>
`;

  return `<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width">
  <title>${esc(PROJECT.title)} - ${esc(PROJECT.edition)} ${esc(PROJECT.version)}</title>
  <style>
${cssText}
  </style>
</head>
<body>

${buildCover()}

${toc}

${chapters.join('\n')}

${buildBackMatter()}

</body>
</html>
`;
}

// ── CLI ──────────────────────────────────────────────────────
if (require.main === module) {
  const chapDir = path.resolve(process.argv[2] || './chapters');
  const outDir  = path.resolve(process.argv[3] || './dist');
  const cssPath = path.resolve(__dirname, 'pdf-styles.css');

  console.log(`\nBuild ${PROJECT.title} ${PROJECT.version} - HTML\n`);

  const html     = buildFullHTML(chapDir, cssPath);
  const htmlPath = path.join(outDir, `${PROJECT.output_basename}.html`);

  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(htmlPath, html, 'utf8');

  const kb = Math.round(Buffer.byteLength(html, 'utf8') / 1024);
  console.log(`\n  ✅  ${htmlPath}  (${kb} KB)\n`);
}

module.exports = { buildFullHTML };
