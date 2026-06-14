/**
 * MYTHIC RINGS v3 — Rendering Engine
 * Converte l'AST dei capitoli in documenti .docx professionali
 * Layout: A5, due colonne, tipografia Georgia
 */

'use strict';

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  PageBreak, AlignmentType, HeadingLevel,
  BorderStyle, WidthType, ShadingType, VerticalAlign, LevelFormat,
  TableOfContents, LineRuleType, SectionType,
  Header, Footer, PageNumber,
} = require('docx');

const path  = require('path');
const fs    = require('fs');
const glob  = require('glob');

const { PAGE, COLORS, FONTS, SIZE, PARA_STYLES,
        borderSingle, borderThick, borderNone,
        bordersAll, bordersNone } = require('./styles');
const { parse, parseFrontmatter, NODE, parseInlineRuns } = require('./md-parser');

// ═══════════════════════════════════════════════════════
// HELPERS RUN / PARAGRAFO
// ═══════════════════════════════════════════════════════
function makeRun(run, overrides = {}) {
  return new TextRun({
    text:    run.text   || '',
    bold:    run.bold   || overrides.bold   || false,
    italics: run.italic || overrides.italic || false,
    font:    FONTS.serif,
    size:    overrides.size  || SIZE.body,
    color:   overrides.color || COLORS.ink,
    ...(run.code ? { highlight: 'yellow', font: 'Courier New', size: SIZE.sm } : {}),
  });
}

function textRun(text, opts = {}) {
  return new TextRun({
    text,
    font: FONTS.serif,
    size:    opts.size   || SIZE.body,
    bold:    opts.bold   || false,
    italics: opts.italic || false,
    color:   opts.color  || COLORS.ink,
    allCaps: opts.caps   || false,
  });
}

function spacerPara(space = 80) {
  return new Paragraph({ children: [], spacing: { before: space, after: space } });
}

function dividerPara(color = COLORS.crimson) {
  return new Paragraph({
    children: [],
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color, space: 1 } },
    spacing: { before: 140, after: 140 },
  });
}

// ═══════════════════════════════════════════════════════
// RENDERER NODI
// ═══════════════════════════════════════════════════════

// ── Heading ─────────────────────────────────────────────
function renderHeading(node) {
  const level = node.level;

  // Fregi decorativi di fine parte: NON sono titoli di sezione e non devono
  // entrare nel TOC. Riconosciuti da: contengono "⟡" oppure sono interamente
  // in corsivo. Resi come paragrafo centrato stilizzato (senza stile Heading).
  const txt = node.runs.map(r => r.text || '').join('');
  const hasOrnament = txt.includes('\u27E1');
  const allItalic = node.runs.length > 0 &&
    node.runs.every(r => r.italic || !(r.text || '').trim());
  if (hasOrnament || allItalic) {
    return new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 220, after: 140 },
      keepLines: true,
      children: node.runs.map(r => new TextRun({
        text: r.text,
        font: FONTS.serif,
        size: hasOrnament ? SIZE.h3 : SIZE.bodyL,
        bold: hasOrnament,
        italics: !hasOrnament,
        color: COLORS.crimson,
        allCaps: false,
      })),
    });
  }

  const headingLevel = [
    HeadingLevel.HEADING_1,
    HeadingLevel.HEADING_2,
    HeadingLevel.HEADING_3,
    HeadingLevel.HEADING_4,
  ][Math.min(level - 1, 3)];

  const styleMap = {
    1: { size: SIZE.chap, color: COLORS.crimson, bold: true, caps: true,
         spacing: { before: 360, after: 160 },
         border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: COLORS.crimson, space: 5 } } },
    2: { size: SIZE.h2,   color: COLORS.midnight, bold: true, caps: false,
         spacing: { before: 240, after: 100 } },
    3: { size: SIZE.h3,   color: COLORS.crimson,  bold: true, italic: true, caps: false,
         spacing: { before: 160, after: 80 } },
    4: { size: SIZE.bodyL, color: COLORS.gray700,  bold: true, caps: false,
         spacing: { before: 120, after: 60 } },
  };

  const s = styleMap[level] || styleMap[3];

  return new Paragraph({
    heading: headingLevel,
    keepNext: true,
    keepLines: true,
    widowControl: true,
    children: node.runs.map(r => new TextRun({
      text:    r.text,
      font:    FONTS.serif,
      size:    s.size,
      bold:    s.bold || r.bold,
      italics: s.italic || r.italic,
      color:   s.color,
      allCaps: s.caps || false,
    })),
    spacing: s.spacing,
    ...(s.border ? { border: s.border } : {}),
  });
}

// ── Paragrafo ───────────────────────────────────────────
function renderParagraph(node, opts = {}) {
  if (!node.runs || node.runs.every(r => !r.text)) return spacerPara(60);
  return new Paragraph({
    children: node.runs.map(r => makeRun(r, { size: opts.size || SIZE.body, color: opts.color })),
    spacing: { before: 60, after: 60, line: 276, lineRule: LineRuleType.AUTO },
    widowControl: true,
    alignment: opts.align || AlignmentType.JUSTIFIED,
    ...(opts.indent ? { indent: opts.indent } : {}),
  });
}

// ── HR ──────────────────────────────────────────────────
function renderHR() {
  return dividerPara();
}

// ── Lista ───────────────────────────────────────────────
function renderList(node, numbering, ref) {
  return node.items.map((item, idx) =>
    new Paragraph({
      numbering: { reference: ref || (node.ordered ? 'numbered' : 'bullets'), level: 0 },
      children: item.runs.map(r => makeRun(r, { size: SIZE.body })),
      spacing: { before: 30, after: 30, line: 264, lineRule: LineRuleType.AUTO },
    })
  );
}

// ── Quote ───────────────────────────────────────────────
function renderQuote(node) {
  const children = node.children.flatMap(child => {
    if (child.type === NODE.PARAGRAPH) {
      return [new Paragraph({
        children: child.runs.map(r => new TextRun({
          text: r.text, font: FONTS.serif, size: SIZE.body,
          italics: true, color: COLORS.gray700,
        })),
        alignment: AlignmentType.CENTER,
        spacing: { before: 60, after: 60 },
        indent: { left: 400, right: 400 },
      })];
    }
    return [];
  });
  return children;
}

// ══════════════════════════════════════════════════════════
// TABELLE
// ══════════════════════════════════════════════════════════
function renderTable(node, tableWidth) {
  const W = tableWidth || PAGE.CONTENT_W;
  const headers = node.headers || [];
  const rows    = node.rows    || [];
  const nCols = Math.max(
    headers.length,
    ...(rows.length ? rows.map(r => r.length) : [1])
  ) || 1;
  // Larghezza colonne PROPORZIONALE al contenuto, espressa in percentuale.
  // La tabella riempie sempre il 100% del contenitore (colonna o pagina piena).
  const cellChars = (cell) => ((cell && cell.runs ? cell.runs : []).map(r => r.text || '').join('')).length;
  const colChars = Array(nCols).fill(1);
  for (const row of [headers, ...rows]) {
    (row || []).forEach((cell, ci) => {
      const len = cellChars(cell);
      if (len > colChars[ci]) colChars[ci] = len;
    });
  }
  // Peso ~ radice quadrata dei caratteri: comprime gli estremi, così le
  // colonne corte non diventano troppo strette e quelle lunghe non dominano.
  const weights = colChars.map(c => Math.sqrt(Math.max(2, Math.min(c, 80))));
  const totW = weights.reduce((a, b) => a + b, 0) || 1;
  const pct = weights.map(w => Math.max(8, Math.round((w / totW) * 100)));
  // Normalizza a 100 esatto
  let pctSum = pct.reduce((a, b) => a + b, 0);
  pct[nCols - 1] += 100 - pctSum;
  // Griglia DXA proporzionale (hint per tblGrid), base = larghezza piena pagina
  const widths = pct.map(p => Math.round((PAGE.CONTENT_W * p) / 100));

  const thinBorder = borderSingle(COLORS.gray300, 2);
  const cellBorders = { top: thinBorder, bottom: thinBorder,
                        left: thinBorder, right: thinBorder };

  const headerRow = headers.length
    ? new TableRow({
        tableHeader: true,
        cantSplit: true,
        children: headers.map((cell, ci) => new TableCell({
          width:    { size: pct[ci], type: WidthType.PERCENTAGE },
          borders:  { top: borderThick(COLORS.crimson, 6), bottom: borderThick(COLORS.crimson, 6),
                      left: thinBorder, right: thinBorder },
          shading:  { fill: COLORS.midnight, type: ShadingType.CLEAR },
          margins:  { top: 70, bottom: 70, left: 60, right: 60 },
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: cell.runs.map(r => new TextRun({
              text: r.text, font: FONTS.serif, size: SIZE.sm,
              bold: true, color: COLORS.white,
            })),
            spacing: { before: 0, after: 0 },
          })],
        })),
      })
    : null;

  const dataRows = rows.map((row, ridx) =>
    new TableRow({
      cantSplit: true,
      children: row.map((cell, ci) => new TableCell({
        width:   { size: pct[ci], type: WidthType.PERCENTAGE },
        borders: cellBorders,
        shading: { fill: ridx % 2 === 0 ? COLORS.white : COLORS.rowAlt, type: ShadingType.CLEAR },
        margins: { top: 55, bottom: 55, left: 60, right: 60 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          alignment: cell.align === 'center' ? AlignmentType.CENTER
                   : cell.align === 'right'  ? AlignmentType.RIGHT
                   : AlignmentType.LEFT,
          children: cell.runs.map(r => makeRun(r, { size: SIZE.sm })),
          spacing: { before: 0, after: 0 },
        })],
      })),
    })
  );

  return new Table({
    width:        { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: widths,
    rows: [
      ...(headerRow ? [headerRow] : []),
      ...dataRows,
    ],
  });
}

// ══════════════════════════════════════════════════════════
// CALLOUT BOX
// ══════════════════════════════════════════════════════════
const BOX_STYLES = {
  warn:    { bg: COLORS.boxWarn,    border: COLORS.gold,    icon: '⚠️ ' },
  info:    { bg: COLORS.boxInfo,    border: COLORS.avalon,  icon: '💡 ' },
  tip:     { bg: COLORS.boxTip,     border: COLORS.ife,     icon: '✅ ' },
  danger:  { bg: COLORS.boxDanger,  border: COLORS.crimson, icon: '🔴 ' },
  example: { bg: COLORS.boxExample, border: COLORS.umbra,   icon: '📖 ' },
  rule:    { bg: COLORS.boxRule,    border: COLORS.crimson, icon: '📏 ' },
  casata_avalon:  { bg: COLORS.avalonLight,  border: COLORS.avalon,  icon: '☀️ ' },
  casata_umbra:   { bg: COLORS.umbraLight,   border: COLORS.umbra,   icon: '🌑 ' },
  casata_ife:     { bg: COLORS.ifeLight,     border: COLORS.ife,     icon: '🌿 ' },
  casata_mictlan: { bg: COLORS.mictlanLight, border: COLORS.mictlan, icon: '💀 ' },
};

function renderBox(node, colWidth, keepTogether = false) {
  const W   = colWidth || PAGE.CONTENT_W;
  const sty = BOX_STYLES[node.boxType] || BOX_STYLES.info;

  const titlePara = node.title
    ? new Paragraph({
        children: [new TextRun({
          text: (sty.icon || '') + node.title,
          font: FONTS.serif, size: SIZE.body,
          bold: true, color: COLORS.crimson,
        })],
        spacing: { before: 40, after: 30 },
      })
    : null;

  const bodyParas = node.children.flatMap(child => {
    if (child.type === NODE.PARAGRAPH) {
      return [new Paragraph({
        children: child.runs.map(r => makeRun(r, { size: SIZE.sm })),
        spacing: { before: 30, after: 30, line: 264, lineRule: LineRuleType.AUTO },
        alignment: AlignmentType.JUSTIFIED,
      })];
    }
    if (child.type === NODE.TABLE || child.type === NODE.TABLE_WIDE) {
      return [renderTable(child, W - 200)];
    }
    if (child.type === NODE.LIST) {
      return renderList(child);
    }
    return [];
  });

  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: [W],
    rows: [new TableRow({
      cantSplit: keepTogether,
      children: [new TableCell({
        width: { size: W, type: WidthType.DXA },
        borders: {
          top:    borderSingle(sty.border, 6),
          bottom: borderSingle(sty.border, 6),
          left:   { style: BorderStyle.SINGLE, size: 14, color: sty.border },
          right:  borderSingle(sty.border, 2),
        },
        shading: { fill: sty.bg, type: ShadingType.CLEAR },
        margins: { top: 90, bottom: 90, left: 160, right: 110 },
        children: [
          ...(titlePara ? [titlePara] : []),
          ...bodyParas,
        ],
      })],
    })],
  });
}

// ══════════════════════════════════════════════════════════
// STAT BLOCK (Bestiario)
// ══════════════════════════════════════════════════════════
function renderStatBlock(node, colWidth) {
  const W = colWidth || PAGE.CONTENT_W;

  // Trova la riga con le statistiche (prima tabella dentro il node)
  const statTable = node.children.find(c => c.type === NODE.TABLE || c.type === NODE.TABLE_WIDE);
  const paragraphs = node.children.filter(c => c.type === NODE.PARAGRAPH);

  const headerPara = new Paragraph({
    children: [
      new TextRun({ text: '⚔️  ', font: FONTS.serif, size: SIZE.bodyL }),
      new TextRun({ text: node.name, font: FONTS.serif, size: SIZE.bodyL,
                    bold: true, color: COLORS.white }),
    ],
    spacing: { before: 30, after: 20 },
  });

  const innerChildren = [
    headerPara,
    ...(statTable ? [renderTable(statTable, W - 160)] : []),
    ...paragraphs.map(p => new Paragraph({
      children: p.runs.map(r => makeRun(r, { size: SIZE.sm })),
      spacing: { before: 25, after: 25 },
    })),
  ];

  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: [W],
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: W, type: WidthType.DXA },
        borders: bordersAll(COLORS.midnight, 4),
        shading: { fill: COLORS.midnight, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: innerChildren,
      })],
    })],
  });
}

// ══════════════════════════════════════════════════════════
// RENDER SEZIONE CAPITOLO
// Ogni capitolo = una sezione: header piena + corpo a 2 colonne
// ══════════════════════════════════════════════════════════
function renderChapterSection(ast, frontmatter, isFirstChapter = false) {
  const { nodes } = ast;

  // ── Intestazione capitolo (sezione a 1 colonna) ──────
  const chapterNum  = frontmatter.chapter || '';
  const chapterTitle = frontmatter.title  || '';
  const partName    = frontmatter.part    || '';
  const epigraph    = frontmatter.epigraph || '';

  const headerChildren = [
    // Banner parte (se presente)
    ...(partName ? [
      new Paragraph({
        children: [textRun(partName.toUpperCase(), {
          size: SIZE.sm, color: COLORS.gold, bold: true,
        })],
        spacing: { before: 0, after: 60 },
      }),
    ] : []),

    // Numero capitolo
    ...(chapterNum ? [
      new Paragraph({
        children: [textRun(`Capitolo ${chapterNum}`, {
          size: SIZE.sm, color: COLORS.gray300, bold: false, italic: true,
        })],
        spacing: { before: 0, after: 40 },
      }),
    ] : []),

    // Titolo capitolo
    new Paragraph({
      children: [textRun(chapterTitle, {
        size: SIZE.chap, color: COLORS.white, bold: true, caps: true,
      })],
      spacing: { before: 60, after: 120 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.gold, space: 8 } },
    }),

    // Epigrafe
    ...(epigraph ? [
      spacerPara(40),
      new Paragraph({
        children: [textRun(`«${epigraph}»`, {
          size: SIZE.body, color: COLORS.parchment2, italic: true,
        })],
        spacing: { before: 40, after: 80 },
        alignment: AlignmentType.CENTER,
        indent: { left: 300, right: 300 },
      }),
    ] : []),

    spacerPara(60),
  ];

  // ── Corpo del capitolo (sezione a 2 colonne) ──────────
  // Separa nodi "wide" (tabelle wide, stat block) dal flusso normale
  // I nodi wide richiedono una micro-sezione a 1 colonna
  const sections = [];
  let currentBlock = [];

  function flushBlock(wide = false) {
    if (currentBlock.length) {
      sections.push({ wide, nodes: currentBlock });
      currentBlock = [];
    }
  }

  // Una tabella normale viene promossa a piena pagina se in una colonna
  // risulterebbe troppo ammassata: molte colonne, molte righe, o celle lunghe.
  function isCrampedTable(n) {
    if (n.type !== NODE.TABLE) return false;
    const headers = n.headers || [];
    const rows = n.rows || [];
    const nCols = Math.max(headers.length, ...(rows.length ? rows.map(r => r.length) : [1])) || 1;
    if (nCols >= 4) return true;
    if (rows.length > 8) return true;
    const maxCell = Math.max(0, ...[headers, ...rows].flatMap(r =>
      (r || []).map(c => ((c && c.runs ? c.runs : []).map(x => x.text || '').join('')).length)));
    if (nCols >= 3 && maxCell >= 40) return true;
    if (maxCell >= 70) return true;
    return false;
  }

  function boxHasCrampedTable(n) {
    if (n.type !== NODE.BOX || !n.children) return false;
    return n.children.some(c => isCrampedTable(c));
  }

  let wideBlock = [];
  function flushWide() {
    if (wideBlock.length) {
      sections.push({ wide: true, nodes: wideBlock });
      wideBlock = [];
    }
  }

  for (const node of nodes) {
    // I nodi wide rompono il flusso a 2 colonne
    const isWide = node.type === NODE.TABLE_WIDE
                || node.type === NODE.STAT_BLOCK
                || isCrampedTable(node)
                || boxHasCrampedTable(node);
    if (isWide) {
      flushBlock(false);   // chiude il blocco a 2 colonne
      wideBlock.push(node); // accumula i wide consecutivi in un'unica sezione piena
    } else {
      flushWide();         // chiude la sezione piena
      currentBlock.push(node);
    }
  }
  flushWide();
  flushBlock(false);

  return { sections, frontmatter };
}

// ══════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════
// HELPER: Header e Footer ricorrenti
// ═══════════════════════════════════════════════════════
function makeHeader(chapterTitle) {
  const title = chapterTitle ? chapterTitle.toUpperCase() : 'MYTHIC RINGS v3.2';
  return new Header({
    children: [new Paragraph({
      children: [
        new TextRun({ text: title, font: FONTS.serif, size: SIZE.xs, color: COLORS.gray500 }),
        new TextRun({ children: ['\t'], font: FONTS.serif }),
        new TextRun({
          children: [PageNumber.CURRENT],
          font: FONTS.serif, size: SIZE.sm, color: COLORS.crimson, bold: true,
        }),
      ],
      border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: COLORS.gray300, space: 4 } },
      tabStops: [{ type: 'right', position: PAGE.CONTENT_W }],
    })],
  });
}

function makeFooter() {
  return new Footer({
    children: [new Paragraph({
      children: [new TextRun({
        text: 'Mythic Rings v3.2  ·  Milano Occulta  ·  Powered by the Apocalypse',
        font: FONTS.serif, size: SIZE.xs, color: COLORS.gray500, italics: true,
      })],
      border: { top: { style: BorderStyle.SINGLE, size: 2, color: COLORS.gray300, space: 4 } },
      alignment: AlignmentType.CENTER,
    })],
  });
}

// Fix 6: intestazione capitolo con sfondo scuro tramite tabella (section shading non supportato)
function makeChapterHeaderTable(chapterTitle, chapterNum, partName, epigraph) {
  const innerChildren = [];
  if (partName) {
    innerChildren.push(new Paragraph({
      children: [new TextRun({ text: partName.toUpperCase(), font: FONTS.serif, size: SIZE.xs, color: COLORS.gold, bold: true })],
      spacing: { before: 0, after: 50 },
    }));
  }
  if (chapterNum) {
    innerChildren.push(new Paragraph({
      children: [new TextRun({ text: `Capitolo ${chapterNum}`, font: FONTS.serif, size: SIZE.sm, color: COLORS.gray300, italics: true })],
      spacing: { before: 0, after: 40 },
    }));
  }
  innerChildren.push(new Paragraph({
    children: [new TextRun({ text: chapterTitle, font: FONTS.serif, size: SIZE.chap, bold: true, color: COLORS.white, allCaps: true })],
    spacing: { before: 0, after: 0 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.gold, space: 8 } },
  }));
  if (epigraph) {
    innerChildren.push(new Paragraph({ children: [], spacing: { before: 60, after: 0 } }));
    innerChildren.push(new Paragraph({
      children: [new TextRun({ text: `«${epigraph}»`, font: FONTS.serif, size: SIZE.body, color: COLORS.parchment2, italics: true })],
      spacing: { before: 40, after: 60 },
      alignment: AlignmentType.CENTER,
    }));
  }
  return new Table({
    width: { size: PAGE.CONTENT_W, type: WidthType.DXA },
    columnWidths: [PAGE.CONTENT_W],
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: PAGE.CONTENT_W, type: WidthType.DXA },
        shading: { fill: COLORS.midnight, type: ShadingType.CLEAR },
        borders: {
          top: borderNone(), bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.crimson },
          left: borderNone(), right: borderNone(),
        },
        margins: { top: 360, bottom: 240, left: 240, right: 240 },
        children: innerChildren,
      })],
    })],
  });
}

// COSTRUZIONE DOCUMENT
// ══════════════════════════════════════════════════════════
function buildDocument(chapters) {
  // chapters: array di { ast, frontmatter, filename }
  const docSections = [];

  // ── Copertina (sezione singola) ─────────────────────
  docSections.push({
    properties: {
      page: {
        size:   { width: PAGE.WIDTH, height: PAGE.HEIGHT },
        margin: { top: 0, bottom: 0, left: 0, right: 0 },
      },
    },
    children: buildCoverPage(),
  });

  // ── Pagina bianca ────────────────────────────────────
  docSections.push({
    properties: {
      page: {
        size: { width: PAGE.WIDTH, height: PAGE.HEIGHT },
        margin: PAGE.MARGIN,
      },
    },
    children: [spacerPara()],
  });

  // ── TOC ──────────────────────────────────────────────
  docSections.push({
    properties: {
      page: { size: { width: PAGE.WIDTH, height: PAGE.HEIGHT }, margin: PAGE.MARGIN },
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [textRun('Indice', { size: SIZE.chap, color: COLORS.crimson, bold: true, caps: true })],
        spacing: { before: 0, after: 200 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: COLORS.crimson, space: 5 } },
      }),
      new TableOfContents('Indice', {
        hyperlink: true,
        headingStyleRange: '1-3',
        stylesWithLevels: [
          { styleName: 'Heading1', level: 1 },
          { styleName: 'Heading2', level: 2 },
          { styleName: 'Heading3', level: 3 },
        ],
      }),
      new Paragraph({ children: [new PageBreak()] }),
    ],
  });

  // ── Capitoli ─────────────────────────────────────────
  for (const ch of chapters) {
    const rendered = renderChapterSection(ch.ast, ch.frontmatter);

    // Sezione intestazione capitolo (1 colonna, header via tabella su sfondo scuro)
    const chHeader = makeChapterHeaderTable(
      ch.frontmatter.title || '',
      ch.frontmatter.chapter || '',
      ch.frontmatter.part || '',
      ch.frontmatter.epigraph || '',
    );
    docSections.push({
      properties: {
        type: SectionType.NEXT_PAGE,
        page: {
          size: { width: PAGE.WIDTH, height: PAGE.HEIGHT },
          margin: PAGE.MARGIN,
        },
        titlePage: false,
      },
      headers: { default: makeHeader(ch.frontmatter.title) },
      footers: { default: makeFooter() },
      children: [chHeader, spacerPara(80)],
    });

    // Sezioni corpo (alternano 2col ↔ 1col per i nodi wide)
    for (const block of rendered.sections) {
      const blockChildren = block.nodes.flatMap(node => renderNode(node, block.wide));

      const chTitle = ch.frontmatter.title || '';
      if (block.wide) {
        // Tabelle wide → 1 colonna, larghezza piena
        docSections.push({
          properties: {
            type: SectionType.CONTINUOUS,
            page: { size: { width: PAGE.WIDTH, height: PAGE.HEIGHT }, margin: PAGE.MARGIN },
            column: { count: 1, space: 0 },
          },
          headers: { default: makeHeader(chTitle) },
          footers: { default: makeFooter() },
          children: [spacerPara(40), ...blockChildren, spacerPara(40)],
        });
      } else {
        // Corpo normale → 2 colonne
        docSections.push({
          properties: {
            type: SectionType.CONTINUOUS,
            page: { size: { width: PAGE.WIDTH, height: PAGE.HEIGHT }, margin: PAGE.MARGIN },
            column: { count: 2, space: PAGE.COL_GAP, equalWidth: true },
          },
          headers: { default: makeHeader(chTitle) },
          footers: { default: makeFooter() },
          children: blockChildren.length ? blockChildren : [spacerPara()],
        });
      }
    }
  }

  // ── Document finale ──────────────────────────────────
  return new Document({
    features: { updateFields: true },
    styles: {
      default: {
        document: { run: { font: FONTS.serif, size: SIZE.body, color: COLORS.ink } },
      },
      paragraphStyles: PARA_STYLES,
    },
    numbering: {
      config: [
        {
          reference: 'bullets',
          levels: [{
            level: 0, format: LevelFormat.BULLET, text: '\u2022',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 480, hanging: 240 } } },
          }],
        },
        {
          reference: 'numbered',
          levels: [{
            level: 0, format: LevelFormat.DECIMAL, text: '%1.',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 480, hanging: 240 } } },
          }],
        },
      ],
    },
    sections: docSections,
  });
}

// ── Render singolo nodo ─────────────────────────────────
function renderNode(node, wideContext = false) {
  const colW = wideContext ? PAGE.CONTENT_W : PAGE.COL_W;

  switch (node.type) {
    case NODE.HEADING:    return [renderHeading(node)];
    case NODE.PARAGRAPH:  return [renderParagraph(node)];
    case NODE.HR:         return [renderHR()];
    case NODE.PAGEBREAK:  return [new Paragraph({ children: [new PageBreak()] })];
    case NODE.COLBREAK:   return [new Paragraph({
      children: [],
      // Column break: inserisce interruzione di colonna nel layout a 2 col
      // docx.js non ha API nativa; usiamo un paragrafo vuoto con spazio grande
      // come segnale visivo al redattore finale
      spacing: { before: 0, after: 0 },
      pageBreakBefore: false,
    })];
    case NODE.LIST:       return renderList(node);
    case NODE.QUOTE:      return renderQuote(node);
    case NODE.BOX:        return [spacerPara(30), renderBox(node, colW, wideContext), spacerPara(30)];
    case NODE.TABLE:
    case NODE.TABLE_WIDE: return [spacerPara(40), renderTable(node, wideContext ? PAGE.CONTENT_W : colW), spacerPara(40)];
    case NODE.STAT_BLOCK: return [spacerPara(40), renderStatBlock(node, colW), spacerPara(40)];
    default:              return [];
  }
}

// ── Copertina ────────────────────────────────────────────
function buildCoverPage() {
  return [
    spacerPara(400),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [textRun('MYTHIC RINGS', { size: 72, bold: true, color: COLORS.crimson, caps: true })],
      spacing: { before: 0, after: 80 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [textRun('v3.2', { size: 40, color: COLORS.gold })],
      spacing: { before: 0, after: 120 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      border: {
        top:    borderSingle(COLORS.crimson, 4),
        bottom: borderSingle(COLORS.crimson, 4),
      },
      children: [textRun('GUARDIANI DI MILANO', {
        size: SIZE.h2, color: COLORS.parchment2, bold: true, caps: true,
      })],
      spacing: { before: 80, after: 80 },
    }),
    spacerPara(80),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [textRun(
        'Un gioco di ruolo di investigazione soprannaturale\n'
        + 'nel cuore di Milano · Powered by the Apocalypse',
        { size: SIZE.body, color: COLORS.gray300, italic: true }
      )],
    }),
  ];
}

// ══════════════════════════════════════════════════════════
// ENTRY POINT
// ══════════════════════════════════════════════════════════

// ── Fix fontTable: docx.js omette la relationship fontTable.xml  ──────────
async function fixFontTableRel(docxPath) {
  const AdmZip = (() => {
    try { return require('adm-zip'); } catch { return null; }
  })();
  
  // Fallback: usa il modulo zip nativo di Node
  const { execSync } = require('child_process');
  const tmpDir = docxPath + '_unzip';
  const fs2 = require('fs');
  
  try {
    // Unzip
    execSync(`unzip -o -q "${docxPath}" -d "${tmpDir}"`, { stdio: 'pipe' });
    
    const relsPath = path.join(tmpDir, 'word', '_rels', 'document.xml.rels');
    if (!fs2.existsSync(relsPath)) return;
    
    let rels = fs2.readFileSync(relsPath, 'utf8');
    const fontTablePath = path.join(tmpDir, 'word', 'fontTable.xml');
    
    if (!rels.includes('fontTable') && fs2.existsSync(fontTablePath)) {
      const rel = '<Relationship Id="rIdFontTable" ' +
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" ' +
        'Target="fontTable.xml"/>';
      rels = rels.replace('</Relationships>', rel + '</Relationships>');
      fs2.writeFileSync(relsPath, rels, 'utf8');
    }
    
    // Rezip
    fs2.unlinkSync(docxPath);
    execSync(`cd "${tmpDir}" && zip -r -q "${docxPath}" .`, { stdio: 'pipe' });
    
  } catch (e) {
    // Fix non critico — logga e continua
    console.warn('  ⚠  fontTable fix skipped:', e.message);
  } finally {
    try { execSync(`rm -rf "${tmpDir}"`); } catch {}
  }
}

async function buildAll(chaptersDir, outputDir) {
  const chalk = require('chalk');

  console.log(chalk.bold.cyan('\n⚙  MYTHIC RINGS v3 — Build Engine\n'));

  // Leggi tutti i capitoli in ordine
  const files = glob.sync(`${chaptersDir}/*.md`).sort();
  if (!files.length) {
    console.error(chalk.red('Nessun file .md trovato in ' + chaptersDir));
    process.exit(1);
  }

  const chapters = [];
  for (const f of files) {
    const raw  = fs.readFileSync(f, 'utf8');
    const { frontmatter, content } = parseFrontmatter(raw);
    const ast = parse(content, frontmatter);
    chapters.push({ ast, frontmatter, filename: path.basename(f) });
    console.log(chalk.green(`  ✓  ${path.basename(f).padEnd(40)} → ${frontmatter.title || '(senza titolo)'}`));
  }

  console.log(chalk.cyan(`\n  Capitoli caricati: ${chapters.length}`));
  console.log(chalk.cyan('  Generazione DOCX in corso...\n'));

  const doc = buildDocument(chapters);
  const buf = await Packer.toBuffer(doc);

  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
  const outPath = path.join(outputDir, 'Mythic_Rings_v3.docx');
  fs.writeFileSync(outPath, buf);
  await fixFontTableRel(outPath);

  const kb = Math.round(buf.length / 1024);
  console.log(chalk.bold.green(`\n  ✅  ${outPath}  (${kb} KB)\n`));
  return outPath;
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
  const chapDir = path.resolve(args[0] || './chapters');
  const outDir  = path.resolve(args[1] || './dist');

  // --chapter <filename> : build solo un capitolo specifico
  const chapterFlag = process.argv.indexOf('--chapter');
  if (chapterFlag !== -1 && process.argv[chapterFlag + 1]) {
    const single = process.argv[chapterFlag + 1];
    const singlePath = path.resolve(chapDir, single);
    if (!fs.existsSync(singlePath)) {
      console.error(`Capitolo non trovato: ${singlePath}`);
      process.exit(1);
    }
    const raw = fs.readFileSync(singlePath, 'utf8');
    const { parseFrontmatter } = require('./md-parser');
    const { frontmatter, content } = parseFrontmatter(raw);
    const ast = parse(content, frontmatter);
    const doc = buildDocument([{ ast, frontmatter, filename: single }]);
    const outFile = path.join(path.resolve(outDir), path.basename(single, '.md') + '.docx');
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
    Packer.toBuffer(doc).then(buf => {
      fs.writeFileSync(outFile, buf);
      console.log(`✅  ${outFile}  (${Math.round(buf.length/1024)} KB)`);
    });
  } else {
    buildAll(chapDir, outDir).catch(e => { console.error(e); process.exit(1); });
  }
}

module.exports = { buildAll, buildDocument, renderNode, renderTable, renderBox };
