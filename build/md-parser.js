/**
 * MYTHIC RINGS v3 — Markdown Parser
 * Converte i file .md dei capitoli in un AST intermedio
 * con supporto per estensioni custom (box, tabelle wide, ecc.)
 *
 * Sintassi custom supportata:
 *
 *   :::box[Titolo del box]{type=warn}
 *   Testo del box...
 *   :::
 *
 *   type = warn | info | tip | danger | example | rule | casata_avalon | casata_umbra | ecc.
 *
 *   :::table-wide
 *   (tabella markdown — verrà resa a larghezza piena, fuori dalle colonne)
 *   :::
 *
 *   :::quote
 *   «Citazione narrativa»
 *   :::
 *
 *   :::stat-block[Nome Creatura]
 *   PF: 15 | Armatura: 1 | Danno: 1d8 | LS: 3
 *   ...
 *   :::
 *
 *   [pagebreak] — forza un'interruzione di pagina
 *   [colbreak]  — forza un'interruzione di colonna
 */

'use strict';

const MarkdownIt = require('markdown-it');
const container = require('markdown-it-container');
const matter    = require('gray-matter');

// ─── Tipi di nodo AST ───────────────────────────────────
const NODE = {
  HEADING:    'heading',
  PARAGRAPH:  'paragraph',
  TABLE:      'table',
  TABLE_WIDE: 'table_wide',
  BOX:        'box',
  QUOTE:      'quote',
  STAT_BLOCK: 'stat_block',
  PAGEBREAK:  'pagebreak',
  COLBREAK:   'colbreak',
  HR:         'hr',
  LIST:       'list',
  LIST_ITEM:  'list_item',
  IMAGE:      'image',
  FRONTMATTER:'frontmatter',
};

// ─── Parser principale ──────────────────────────────────
function createParser() {
  const md = new MarkdownIt({
    html: false,
    linkify: false,
    typographer: true,
  });

  // Container generico :::box[...]{...}
  md.use(container, 'box', {
    validate(params) { return params.trim().startsWith('box'); },
    render(tokens, idx) {
      if (tokens[idx].nesting === 1) {
        const info = tokens[idx].info.trim().slice(3).trim();
        const titleMatch = info.match(/^\[([^\]]*)\]/);
        const typeMatch  = info.match(/\{type=([^}]+)\}/);
        const title = titleMatch ? titleMatch[1] : '';
        const type  = typeMatch  ? typeMatch[1]  : 'info';
        return `<box type="${type}" title="${title}">`;
      }
      return '</box>';
    },
  });

  // Container per tabelle wide
  md.use(container, 'table-wide', {
    validate(params) { return params.trim() === 'table-wide'; },
    render(tokens, idx) {
      return tokens[idx].nesting === 1 ? '<table-wide>' : '</table-wide>';
    },
  });

  // Container per quote narrative
  md.use(container, 'quote', {
    validate(params) { return params.trim() === 'quote'; },
    render(tokens, idx) {
      return tokens[idx].nesting === 1 ? '<quote>' : '</quote>';
    },
  });

  // Container per stat block
  md.use(container, 'stat-block', {
    validate(params) { return params.trim().startsWith('stat-block'); },
    render(tokens, idx) {
      if (tokens[idx].nesting === 1) {
        const nameMatch = tokens[idx].info.trim().match(/\[([^\]]+)\]/);
        const name = nameMatch ? nameMatch[1] : 'Creatura';
        return `<stat-block name="${name}">`;
      }
      return '</stat-block>';
    },
  });

  return md;
}

// ─── Tokenizza gli inline runs ──────────────────────────
function parseInlineRuns(html) {
  // Converte HTML inline in lista di run: [{text, bold, italic, color, size}]
  const runs = [];
  let i = 0;
  let bold = false, italic = false, code = false;

  // Strip HTML tags semplici e colleziona run
  const re = /<(\/?)([a-z]+)([^>]*)>|([^<]+)/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    if (m[4] !== undefined) {
      // Testo puro
      const text = m[4]
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/&ldquo;/g, '\u201C')
        .replace(/&rdquo;/g, '\u201D')
        .replace(/&laquo;/g, '\u00AB')
        .replace(/&raquo;/g, '\u00BB')
        .replace(/&mdash;/g, '\u2014')
        .replace(/&ndash;/g, '\u2013')
        .replace(/&hellip;/g, '\u2026');
      if (text) runs.push({ text, bold, italic, code });
    } else {
      const closing = m[1] === '/';
      const tag = m[2].toLowerCase();
      if (tag === 'strong' || tag === 'b') bold = !closing;
      else if (tag === 'em' || tag === 'i') italic = !closing;
      else if (tag === 'code') code = !closing;
      else if (tag === 'br') runs.push({ text: '\n', bold, italic, code });
    }
  }

  return runs.length ? runs : [{ text: '', bold: false, italic: false, code: false }];
}

// ─── Parsing tabella markdown ───────────────────────────
function parseTable(token, tokens, idx) {
  // Ricostruisce header e righe dalla sequenza di token markdown-it
  const headers = [];
  const rows = [];
  let currentRow = [];
  let inHeader = false;
  let inBody = false;

  for (let j = idx; j < tokens.length; j++) {
    const t = tokens[j];
    if (t.type === 'table_close') break;
    if (t.type === 'thead_open')  { inHeader = true; inBody = false; }
    if (t.type === 'thead_close') { inHeader = false; }
    if (t.type === 'tbody_open')  { inBody = true; }
    if (t.type === 'tr_close') {
      if (inHeader) headers.push(...currentRow);
      else if (inBody) rows.push([...currentRow]);
      currentRow = [];
    }
    if (t.type === 'th' || t.type === 'td') {
      // Contenuto inline del token
      currentRow.push({
        runs: parseInlineRuns(t.children ? renderInline(t.children) : ''),
        align: t.attrGet ? (t.attrGet('style') || '').replace('text-align:', '').trim() : 'left',
      });
    }
    if ((t.type === 'inline') && currentRow.length === 0) {
      // Fallback
    }
  }
  return { headers, rows };
}

// Render inline token array to HTML string
function renderInline(tokens) {
  return tokens.map(t => {
    if (t.type === 'text') return t.content;
    if (t.type === 'strong_open') return '<strong>';
    if (t.type === 'strong_close') return '</strong>';
    if (t.type === 'em_open') return '<em>';
    if (t.type === 'em_close') return '</em>';
    if (t.type === 'code_inline') return `<code>${t.content}</code>`;
    if (t.type === 'softbreak') return ' ';
    if (t.type === 'hardbreak') return '<br>';
    return t.content || '';
  }).join('');
}

// ─── Parser principale: MD → AST custom ────────────────
function parse(markdownText, frontmatter = {}) {
  const md = createParser();
  const tokens = md.parse(markdownText, {});
  const ast = [];

  // Stato per container custom
  let inBox = false, boxType = 'info', boxTitle = '', boxChildren = [];
  let inTableWide = false, tableWideChildren = [];
  let inQuote = false, quoteChildren = [];
  let inStatBlock = false, statBlockName = '', statBlockChildren = [];

  function flushBox() {
    if (inBox) {
      ast.push({ type: NODE.BOX, boxType, title: boxTitle, children: boxChildren });
      inBox = false; boxChildren = [];
    }
  }
  function flushTableWide() {
    if (inTableWide) {
      ast.push({ type: NODE.TABLE_WIDE, children: tableWideChildren });
      inTableWide = false; tableWideChildren = [];
    }
  }
  function flushQuote() {
    if (inQuote) {
      ast.push({ type: NODE.QUOTE, children: quoteChildren });
      inQuote = false; quoteChildren = [];
    }
  }
  function flushStatBlock() {
    if (inStatBlock) {
      ast.push({ type: NODE.STAT_BLOCK, name: statBlockName, children: statBlockChildren });
      inStatBlock = false; statBlockChildren = [];
    }
  }

  let i = 0;
  while (i < tokens.length) {
    const tok = tokens[i];

    // ── Container custom: apertura ──────────────────
    if (tok.type === 'container_box_open') {
      flushBox();
      const info = tok.info.trim().slice(3).trim();
      const titleM = info.match(/^\[([^\]]*)\]/);
      const typeM  = info.match(/\{type=([^}]+)\}/);
      boxTitle = titleM ? titleM[1] : '';
      boxType  = typeM  ? typeM[1]  : 'info';
      inBox = true; i++; continue;
    }
    if (tok.type === 'container_box_close') {
      flushBox(); i++; continue;
    }
    if (tok.type === 'container_table-wide_open') {
      flushTableWide(); inTableWide = true; i++; continue;
    }
    if (tok.type === 'container_table-wide_close') {
      flushTableWide(); i++; continue;
    }
    if (tok.type === 'container_quote_open') {
      flushQuote(); inQuote = true; i++; continue;
    }
    if (tok.type === 'container_quote_close') {
      flushQuote(); i++; continue;
    }
    if (tok.type === 'container_stat-block_open') {
      flushStatBlock();
      const nm = tok.info.trim().match(/\[([^\]]+)\]/);
      statBlockName = nm ? nm[1] : 'Creatura';
      inStatBlock = true; i++; continue;
    }
    if (tok.type === 'container_stat-block_close') {
      flushStatBlock(); i++; continue;
    }

    // ── Heading ────────────────────────────────────
    if (tok.type === 'heading_open') {
      const level = parseInt(tok.tag.slice(1), 10);
      const inlineTok = tokens[i + 1];
      const text = inlineTok ? renderInline(inlineTok.children || []) : '';
      const node = { type: NODE.HEADING, level, runs: parseInlineRuns(text) };
      if (inBox) boxChildren.push(node);
      else if (inTableWide) tableWideChildren.push(node);
      else if (inQuote) quoteChildren.push(node);
      else if (inStatBlock) statBlockChildren.push(node);
      else ast.push(node);
      i += 3; continue; // open + inline + close
    }

    // ── Paragraph ──────────────────────────────────
    if (tok.type === 'paragraph_open') {
      const inlineTok = tokens[i + 1];
      const text = inlineTok ? renderInline(inlineTok.children || []) : '';

      // Controllo comandi speciali
      const stripped = text.trim();
      if (stripped === '[pagebreak]') {
        const node = { type: NODE.PAGEBREAK };
        if (inBox) boxChildren.push(node);
        else ast.push(node);
        i += 3; continue;
      }
      if (stripped === '[colbreak]') {
        ast.push({ type: NODE.COLBREAK });
        i += 3; continue;
      }

      const node = { type: NODE.PARAGRAPH, runs: parseInlineRuns(text) };
      if (inBox) boxChildren.push(node);
      else if (inTableWide) tableWideChildren.push(node);
      else if (inQuote) quoteChildren.push(node);
      else if (inStatBlock) statBlockChildren.push(node);
      else ast.push(node);
      i += 3; continue;
    }

    // ── Table ──────────────────────────────────────
    if (tok.type === 'table_open') {
      const tbl = parseTableTokens(tokens, i);
      const node = { type: inTableWide ? NODE.TABLE_WIDE : NODE.TABLE, ...tbl };
      if (inBox) boxChildren.push(node);
      else if (inStatBlock) statBlockChildren.push(node);
      else ast.push(node);
      // Avanza oltre tutti i token della tabella
      let depth = 0;
      while (i < tokens.length) {
        if (tokens[i].type === 'table_open')  depth++;
        if (tokens[i].type === 'table_close') { depth--; if (depth === 0) { i++; break; } }
        i++;
      }
      continue;
    }

    // ── HR ─────────────────────────────────────────
    if (tok.type === 'hr') {
      ast.push({ type: NODE.HR });
    }

    // ── Liste ──────────────────────────────────────
    if (tok.type === 'bullet_list_open' || tok.type === 'ordered_list_open') {
      const ordered = tok.type === 'ordered_list_open';
      const items = [];
      let j = i + 1, depth = 1;
      while (j < tokens.length && depth > 0) {
        const t = tokens[j];
        if (t.type === 'bullet_list_open' || t.type === 'ordered_list_open') depth++;
        if (t.type === 'bullet_list_close' || t.type === 'ordered_list_close') {
          depth--;
          if (depth === 0) { j++; break; }
        }
        if (t.type === 'inline' && depth === 1) {
          items.push({ runs: parseInlineRuns(renderInline(t.children || [])) });
        }
        j++;
      }
      const node = { type: NODE.LIST, ordered, items };
      if (inBox) boxChildren.push(node);
      else ast.push(node);
      i = j; continue;
    }

    i++;
  }

  // Flush pending containers
  flushBox(); flushTableWide(); flushQuote(); flushStatBlock();

  return { frontmatter, nodes: ast };
}

// Parsing tabella dedicato
function parseTableTokens(tokens, startIdx) {
  const headers = [];
  const rows    = [];
  let currentRow = null;
  let inHeader = false;

  for (let i = startIdx; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.type === 'table_close') break;
    if (t.type === 'thead_open')  inHeader = true;
    if (t.type === 'thead_close') inHeader = false;
    if (t.type === 'tr_open')  currentRow = [];
    if (t.type === 'tr_close') {
      if (currentRow) {
        if (inHeader) headers.push(...currentRow);
        else rows.push(currentRow);
        currentRow = null;
      }
    }
    if ((t.type === 'th' || t.type === 'td') && currentRow !== null) {
      const inline = tokens[i + 1];
      const text = inline && inline.type === 'inline'
        ? renderInline(inline.children || []) : '';
      const align = (t.attrGet('style') || '').replace('text-align:', '').trim() || 'left';
      currentRow.push({ runs: parseInlineRuns(text), align });
      i++; // salta l'inline
    }
  }

  return { headers, rows };
}

// ─── Parsing frontmatter YAML ───────────────────────────
function parseFrontmatter(rawText) {
  const parsed = matter(rawText);
  return { frontmatter: parsed.data, content: parsed.content };
}

module.exports = { parse, parseFrontmatter, NODE, parseInlineRuns };
