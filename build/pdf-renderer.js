/**
 * MYTHIC RINGS v3 — PDF HTML Renderer
 * Converte i capitoli .md in un documento HTML completo
 * pronto per WeasyPrint → PDF A5 due colonne
 */
'use strict';

const fs   = require('fs');
const path = require('path');
const glob = require('glob');
const { parseFrontmatter, parse, NODE } = require('./md-parser');

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
  <div class="cover-eyebrow">Urban Fantasy · Milano Occulta</div>
  <div class="cover-title">Mythic<br>Rings</div>
  <div class="cover-version">v 3.1</div>
  <div class="cover-rule"></div>
  <div class="cover-subtitle">
    Guardiani di Milano<br>
    <br>
    Un gioco di ruolo di investigazione soprannaturale<br>
    nel cuore di Milano
  </div>
  <div class="cover-tagline">Powered by the Apocalypse</div>
</div>
`;
}

// ── Documento HTML completo ──────────────────────────────────
function buildFullHTML(chaptersDir, cssPath) {
  const files = glob.sync(`${chaptersDir}/*.md`).sort();
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
  <title>Mythic Rings v3.1</title>
  <style>
${cssText}
  </style>
</head>
<body>

${buildCover()}

<div class="blank-page"></div>

${toc}

${chapters.join('\n')}

</body>
</html>
`;
}

// ── CLI ──────────────────────────────────────────────────────
if (require.main === module) {
  const chapDir = path.resolve(process.argv[2] || './chapters');
  const outDir  = path.resolve(process.argv[3] || './dist');
  const cssPath = path.resolve(__dirname, 'pdf-styles.css');

  console.log('\n🖋  MYTHIC RINGS v3 — PDF HTML Renderer\n');

  const html     = buildFullHTML(chapDir, cssPath);
  const htmlPath = path.join(outDir, 'Mythic_Rings_v3.html');

  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(htmlPath, html, 'utf8');

  const kb = Math.round(Buffer.byteLength(html, 'utf8') / 1024);
  console.log(`\n  ✅  ${htmlPath}  (${kb} KB)\n`);
}

module.exports = { buildFullHTML };
