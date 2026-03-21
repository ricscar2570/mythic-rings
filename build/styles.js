/**
 * MYTHIC RINGS v3 — Design System
 * Palette, tipografia, dimensioni pagina, stili Word
 * Tutti i valori in DXA (1 inch = 1440 DXA, 1 mm = 56.7 DXA)
 */

// ═══════════════════════════════════════════════════════
// PAGINA A5
// ═══════════════════════════════════════════════════════
const PAGE = {
  WIDTH:  8395,   // 148mm
  HEIGHT: 11906,  // 210mm
  MARGIN: {
    top:    1020,  // 18mm
    bottom: 1020,  // 18mm
    left:   980,   // 17mm — colonna sinistra
    right:  980,   // 17mm — colonna destra
    gutter: 0,
  },
  // Larghezza area contenuto
  get CONTENT_W() { return this.WIDTH - this.MARGIN.left - this.MARGIN.right; }, // ~6435
  // Colonne: due colonne + gap
  COL_GAP:  360,   // 6mm tra le colonne
  get COL_W() { return Math.floor((this.CONTENT_W - this.COL_GAP) / 2); }, // ~3037
};

// ═══════════════════════════════════════════════════════
// PALETTE COLORI
// ═══════════════════════════════════════════════════════
const COLORS = {
  // Base
  ink:         '1A1A1A',
  white:       'FFFFFF',
  parchment:   'F8F3EC',
  parchment2:  'F0E8D8',

  // Brand primario
  crimson:     '8B0000',   // rosso scuro — titoli, accenti primari
  crimsonLight:'C0392B',
  gold:        'B8860B',   // oro — decorazioni, callout border
  goldLight:   'D4A017',
  midnight:    '1A1A2E',   // sfondo scuro — header capitoli

  // Grigi
  gray900:     '1A1A1A',
  gray700:     '444444',
  gray500:     '777777',
  gray300:     'BBBBBB',
  gray100:     'F0F0F0',

  // Sfumature tematiche per Casate
  avalon:      '1A3A6A',   // blu reale
  avalonLight: 'EEF4FF',
  umbra:       '2D0052',   // viola notte
  umbraLight:  'F3EEFF',
  ife:         '0D3D0D',   // verde foresta
  ifeLight:    'EDFDED',
  mictlan:     '1A0A2E',   // blu notte profondo
  mictlanLight:'EEF0FF',

  // Callout box
  boxWarn:     'FFF8E8',   // sfondo avviso
  boxInfo:     'E8F4FF',   // sfondo info
  boxTip:      'E8FFF0',   // sfondo suggerimento
  boxDanger:   'FFE8E8',   // sfondo pericolo
  boxExample:  'F5F0FF',   // sfondo esempio
  boxRule:     'FFF0F5',   // sfondo regola

  // Row alternation
  rowAlt:      'F7F3EE',
};

// ═══════════════════════════════════════════════════════
// TIPOGRAFIA
// ═══════════════════════════════════════════════════════
const FONTS = {
  serif:  'Georgia',        // corpo testo, tutto il manuale
  sansSerif: 'Arial',       // fallback
};

// Dimensioni in halfpoints (1pt = 2 halfpoints)
const SIZE = {
  xs:    16,  // 8pt   — note a pie' di pagina
  sm:    18,  // 9pt   — didascalie, note
  body:  20,  // 10pt  — corpo testo standard
  bodyL: 22,  // 11pt  — corpo testo ampio
  h3:    22,  // 11pt  — intestazione h3
  h2:    26,  // 13pt  — intestazione h2
  h1:    32,  // 16pt  — intestazione h1
  chap:  40,  // 20pt  — titolo capitolo
  title: 52,  // 26pt  — titolo parte/copertina
};

// ═══════════════════════════════════════════════════════
// STILI WORD (paragrafo e run)
// ═══════════════════════════════════════════════════════
const { AlignmentType, HeadingLevel, BorderStyle, ShadingType,
        LineRuleType } = require('docx');

const PARA_STYLES = [
  // ── Heading 1 (titolo capitolo) ──────────────────────
  {
    id: 'Heading1', name: 'Heading 1',
    basedOn: 'Normal', next: 'Normal',
    quickFormat: true,
    run: {
      font: FONTS.serif, size: SIZE.chap,
      bold: true, color: COLORS.crimson, allCaps: true,
    },
    paragraph: {
      spacing: { before: 400, after: 180 },
      outlineLevel: 0,
      border: {
        bottom: { style: BorderStyle.SINGLE, size: 8, color: COLORS.crimson, space: 6 },
      },
    },
  },

  // ── Heading 2 (sezione) ──────────────────────────────
  {
    id: 'Heading2', name: 'Heading 2',
    basedOn: 'Normal', next: 'Normal',
    quickFormat: true,
    run: {
      font: FONTS.serif, size: SIZE.h2,
      bold: true, color: COLORS.midnight,
    },
    paragraph: {
      spacing: { before: 260, after: 100 },
      outlineLevel: 1,
    },
  },

  // ── Heading 3 (sottosezione) ─────────────────────────
  {
    id: 'Heading3', name: 'Heading 3',
    basedOn: 'Normal', next: 'Normal',
    quickFormat: true,
    run: {
      font: FONTS.serif, size: SIZE.h3,
      bold: true, italics: true, color: COLORS.crimson,
    },
    paragraph: {
      spacing: { before: 180, after: 80 },
      outlineLevel: 2,
    },
  },

  // ── Corpo testo ──────────────────────────────────────
  {
    id: 'BodyText', name: 'Body Text',
    basedOn: 'Normal', next: 'BodyText',
    run: { font: FONTS.serif, size: SIZE.body, color: COLORS.ink },
    paragraph: {
      spacing: { before: 60, after: 60, line: 276, lineRule: LineRuleType.AUTO },
      alignment: AlignmentType.JUSTIFIED,
    },
  },

  // ── Testo callout box ────────────────────────────────
  {
    id: 'BoxText', name: 'Box Text',
    basedOn: 'Normal', next: 'BoxText',
    run: { font: FONTS.serif, size: SIZE.sm, color: COLORS.ink },
    paragraph: {
      spacing: { before: 40, after: 40, line: 264, lineRule: LineRuleType.AUTO },
      alignment: AlignmentType.JUSTIFIED,
    },
  },

  // ── Intestazione box ────────────────────────────────
  {
    id: 'BoxTitle', name: 'Box Title',
    basedOn: 'Normal', next: 'BoxText',
    run: { font: FONTS.serif, size: SIZE.body, bold: true, color: COLORS.crimson },
    paragraph: { spacing: { before: 40, after: 30 } },
  },

  // ── Citazione/Quote ─────────────────────────────────
  {
    id: 'Quote', name: 'Quote',
    basedOn: 'Normal', next: 'BodyText',
    run: { font: FONTS.serif, size: SIZE.body, italics: true, color: COLORS.gray700 },
    paragraph: {
      spacing: { before: 120, after: 120 },
      indent: { left: 480, right: 480 },
      alignment: AlignmentType.CENTER,
    },
  },

  // ── Nota a pie' di pagina ────────────────────────────
  {
    id: 'FootNote', name: 'FootNote',
    basedOn: 'Normal',
    run: { font: FONTS.serif, size: SIZE.xs, color: COLORS.gray500 },
    paragraph: { spacing: { before: 0, after: 0 } },
  },

  // ── Testo tabella header ─────────────────────────────
  {
    id: 'TableHeader', name: 'Table Header',
    basedOn: 'Normal',
    run: { font: FONTS.serif, size: SIZE.sm, bold: true, color: COLORS.white },
    paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 } },
  },

  // ── Testo tabella cella ──────────────────────────────
  {
    id: 'TableCell', name: 'Table Cell',
    basedOn: 'Normal',
    run: { font: FONTS.serif, size: SIZE.sm, color: COLORS.ink },
    paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 50, after: 50 } },
  },
];

// ═══════════════════════════════════════════════════════
// BORDER HELPERS
// ═══════════════════════════════════════════════════════
function borderSingle(color, size = 4) {
  return { style: BorderStyle.SINGLE, size, color };
}
function borderThick(color, size = 8) {
  return { style: BorderStyle.SINGLE, size, color };
}
function borderNone() {
  return { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
}
function bordersAll(color, size = 2) {
  const b = borderSingle(color, size);
  return { top: b, bottom: b, left: b, right: b };
}
function bordersNone() {
  const b = borderNone();
  return { top: b, bottom: b, left: b, right: b };
}

module.exports = {
  PAGE, COLORS, FONTS, SIZE, PARA_STYLES,
  borderSingle, borderThick, borderNone, bordersAll, bordersNone,
  AlignmentType, HeadingLevel, BorderStyle, ShadingType,
};
