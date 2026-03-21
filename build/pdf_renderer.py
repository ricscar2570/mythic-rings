#!/usr/bin/env python3
"""
MYTHIC RINGS v3 — PDF Renderer
Pipeline diretta: .md → HTML → PDF con WeasyPrint

Layout professionale PbtA:
  - A5, due colonne, margini calibrati
  - EB Garamond (corpo) + Cinzel (titoli)
  - Intestazioni capitolo su sfondo scuro a piena pagina
  - Callout box, tabelle, stat block bestiario
  - Numeri pagina, testatine correnti
  - Segnalibri PDF, TOC cliccabile
"""

import os, sys, re, glob, json
from pathlib import Path
from datetime import datetime

import markdown_it
from markdown_it import MarkdownIt
from markdown_it.token import Token
import yaml   # per frontmatter
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# ─── Percorsi ────────────────────────────────────────────
BASE     = Path(__file__).parent.parent
CHAPTERS = BASE / 'chapters'
DIST     = BASE / 'dist'
ASSETS   = BASE / 'assets'
FONTS    = ASSETS / 'fonts'


# ═══════════════════════════════════════════════════════════
# CSS — Design System completo
# ═══════════════════════════════════════════════════════════
def build_css(fonts_dir: Path) -> str:
    fonts_url = fonts_dir.resolve().as_uri()
    return f"""
/* ── Font faces ─────────────────────────────────────── */
@font-face {{
    font-family: 'EB Garamond';
    font-style: normal;
    font-weight: 400;
    src: url('{fonts_url}/EBGaramond-Regular.woff2') format('woff2');
}}
@font-face {{
    font-family: 'EB Garamond';
    font-style: italic;
    font-weight: 400;
    src: url('{fonts_url}/EBGaramond-Italic.woff2') format('woff2');
}}
@font-face {{
    font-family: 'EB Garamond';
    font-style: normal;
    font-weight: 700;
    src: url('{fonts_url}/EBGaramond-Bold.woff2') format('woff2');
}}
@font-face {{
    font-family: 'EB Garamond';
    font-style: italic;
    font-weight: 700;
    src: url('{fonts_url}/EBGaramond-BoldItalic.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Cinzel';
    font-style: normal;
    font-weight: 400;
    src: url('{fonts_url}/Cinzel-Regular.woff2') format('woff2');
}}
@font-face {{
    font-family: 'Cinzel';
    font-style: normal;
    font-weight: 700;
    src: url('{fonts_url}/Cinzel-Bold.woff2') format('woff2');
}}

/* ── Variabili colore ───────────────────────────────── */
:root {{
    --ink:          #1a1a1a;
    --ink-light:    #444444;
    --crimson:      #8b0000;
    --crimson-mid:  #a30000;
    --gold:         #b8860b;
    --gold-light:   #d4a017;
    --midnight:     #1a1a2e;
    --midnight2:    #16213e;
    --parchment:    #f8f3ec;
    --parchment2:   #f0e8d8;
    --white:        #ffffff;
    --gray-light:   #f0f0f0;
    --gray-mid:     #999999;
    --gray-dark:    #555555;
    /* box backgrounds */
    --box-warn:     #fff8e8;
    --box-info:     #e8f4ff;
    --box-tip:      #e8fff0;
    --box-danger:   #ffe8e8;
    --box-example:  #f5f0ff;
    --box-rule:     #fff0f5;
    --box-avalon:   #eef4ff;
    --box-umbra:    #f3eeff;
    --box-ife:      #edfded;
    --box-mictlan:  #eef0ff;
    /* box accents */
    --accent-warn:    #b8860b;
    --accent-info:    #1a3a6a;
    --accent-tip:     #0d3d0d;
    --accent-danger:  #8b0000;
    --accent-example: #2d0052;
    --accent-rule:    #8b0000;
    --accent-avalon:  #1a3a6a;
    --accent-umbra:   #2d0052;
    --accent-ife:     #0d3d0d;
    --accent-mictlan: #1a0a2e;
}}

/* ── Pagina A5 ─────────────────────────────────────── */
@page {{
    size: 148mm 210mm;
    margin: 16mm 14mm 18mm 14mm;

    @top-center {{
        content: string(chapter-title);
        font-family: 'EB Garamond', serif;
        font-size: 7.5pt;
        color: var(--gray-mid);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border-bottom: 0.3pt solid var(--gray-mid);
        padding-bottom: 2mm;
        width: 100%;
        text-align: center;
    }}
    @bottom-center {{
        content: counter(page);
        font-family: 'Cinzel', serif;
        font-size: 8.5pt;
        color: var(--crimson);
        font-weight: 700;
    }}
}}

@page :first {{
    margin: 0;
    @top-center {{ content: none; }}
    @bottom-center {{ content: none; }}
}}

@page chapter-cover {{
    margin: 0;
    @top-center {{ content: none; }}
    @bottom-center {{ content: none; }}
}}

/* ── Reset & base ──────────────────────────────────── */
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: 'EB Garamond', 'DejaVu Serif', serif;
    font-size: 9.5pt;
    line-height: 1.45;
    color: var(--ink);
    background: var(--white);
    text-rendering: optimizeLegibility;
    font-kerning: normal;
    font-variant-ligatures: common-ligatures;
    -webkit-font-smoothing: antialiased;
}}

/* ── Layout documento ──────────────────────────────── */
.document {{
    width: 100%;
}}

/* ── Copertina ─────────────────────────────────────── */
.cover-page {{
    page: chapter-cover;
    width:  148mm;
    height: 210mm;
    background: var(--midnight);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20mm;
    page-break-after: always;
}}

.cover-title {{
    font-family: 'Cinzel', serif;
    font-size: 32pt;
    font-weight: 700;
    color: var(--white);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4mm;
    line-height: 1.1;
}}

.cover-subtitle {{
    font-family: 'Cinzel', serif;
    font-size: 11pt;
    color: var(--gold-light);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 8mm;
    border-top: 0.5pt solid var(--gold);
    border-bottom: 0.5pt solid var(--gold);
    padding: 3mm 0;
    width: 80%;
}}

.cover-desc {{
    font-family: 'EB Garamond', serif;
    font-size: 9.5pt;
    color: #cccccc;
    font-style: italic;
    line-height: 1.6;
    max-width: 90%;
}}

.cover-ornament {{
    font-size: 24pt;
    color: var(--gold);
    margin: 6mm 0;
    letter-spacing: 0.3em;
}}

/* ── Pagina bianca ─────────────────────────────────── */
.blank-page {{
    page-break-after: always;
    height: 210mm;
}}

/* ── TOC ───────────────────────────────────────────── */
.toc-page {{
    page-break-after: always;
    padding: 0;
}}

.toc-title {{
    font-family: 'Cinzel', serif;
    font-size: 16pt;
    font-weight: 700;
    color: var(--crimson);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-bottom: 2pt solid var(--crimson);
    padding-bottom: 3mm;
    margin-bottom: 6mm;
}}

.toc-entry {{
    display: flex;
    align-items: baseline;
    margin-bottom: 1.5mm;
    font-size: 8.5pt;
    line-height: 1.3;
}}

.toc-entry.part {{
    font-family: 'Cinzel', serif;
    font-size: 7.5pt;
    font-weight: 700;
    color: var(--crimson);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4mm;
    margin-bottom: 1mm;
    border-bottom: 0.3pt solid var(--crimson);
    padding-bottom: 0.5mm;
}}

.toc-entry.chapter {{
    font-family: 'EB Garamond', serif;
    color: var(--ink);
}}

.toc-num {{
    color: var(--crimson);
    font-family: 'Cinzel', serif;
    font-size: 7.5pt;
    font-weight: 700;
    min-width: 8mm;
    flex-shrink: 0;
}}

.toc-name {{
    flex: 1;
    padding: 0 2mm;
}}

.toc-dots {{
    flex: 1;
    border-bottom: 0.3pt dotted var(--gray-mid);
    margin: 0 2mm;
    min-width: 4mm;
    position: relative;
    bottom: 0.8mm;
}}

.toc-page-num {{
    color: var(--crimson);
    font-family: 'Cinzel', serif;
    font-size: 7.5pt;
    font-weight: 700;
    min-width: 6mm;
    text-align: right;
}}

/* ── Intestazione capitolo (full-bleed dark) ─────── */
.chapter-header {{
    page: chapter-cover;
    width: 148mm;
    min-height: 52mm;
    background: var(--midnight);
    padding: 12mm 14mm 10mm 14mm;
    page-break-before: always;
    page-break-after: always;
}}

.chapter-part-label {{
    font-family: 'Cinzel', serif;
    font-size: 6.5pt;
    color: var(--gold);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 2mm;
}}

.chapter-num {{
    font-family: 'EB Garamond', serif;
    font-size: 8pt;
    color: #888888;
    font-style: italic;
    margin-bottom: 1.5mm;
}}

.chapter-title {{
    font-family: 'Cinzel', serif;
    font-size: 20pt;
    font-weight: 700;
    color: var(--white);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    line-height: 1.1;
    border-bottom: 1.5pt solid var(--gold);
    padding-bottom: 3mm;
    margin-bottom: 4mm;
    string-set: chapter-title content();
}}

.chapter-epigraph {{
    font-family: 'EB Garamond', serif;
    font-size: 9pt;
    color: #cccccc;
    font-style: italic;
    text-align: center;
    line-height: 1.5;
    padding: 0 10mm;
}}

/* ── Corpo a due colonne ───────────────────────────── */
.chapter-body {{
    column-count: 2;
    column-gap: 5mm;
    column-rule: 0.3pt solid #dddddd;
    column-fill: balance;
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
    orphans: 3;
    widows: 3;
}}

/* ── Headings nel corpo ────────────────────────────── */
.chapter-body h2 {{
    font-family: 'Cinzel', serif;
    font-size: 11.5pt;
    font-weight: 700;
    color: var(--midnight);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 0.5pt solid var(--crimson);
    padding-bottom: 1mm;
    margin-top: 5mm;
    margin-bottom: 2mm;
    column-span: none;
    break-after: avoid;
    line-height: 1.2;
}}

.chapter-body h3 {{
    font-family: 'Cinzel', serif;
    font-size: 9.5pt;
    font-weight: 700;
    color: var(--crimson);
    letter-spacing: 0.04em;
    margin-top: 3.5mm;
    margin-bottom: 1.5mm;
    break-after: avoid;
    line-height: 1.2;
}}

.chapter-body h4 {{
    font-family: 'EB Garamond', serif;
    font-size: 9.5pt;
    font-weight: 700;
    font-style: italic;
    color: var(--gray-dark);
    margin-top: 2.5mm;
    margin-bottom: 1mm;
    break-after: avoid;
}}

/* ── Paragrafi ─────────────────────────────────────── */
.chapter-body p {{
    margin-bottom: 1.8mm;
    text-indent: 3mm;
    line-height: 1.45;
}}

.chapter-body p:first-of-type,
.chapter-body h2 + p,
.chapter-body h3 + p,
.chapter-body h4 + p {{
    text-indent: 0;
}}

/* ── Liste ─────────────────────────────────────────── */
.chapter-body ul,
.chapter-body ol {{
    margin: 1.5mm 0 1.5mm 4mm;
    padding-left: 3mm;
}}

.chapter-body li {{
    margin-bottom: 1mm;
    line-height: 1.4;
    text-indent: 0;
}}

.chapter-body ul li::marker {{
    color: var(--crimson);
    content: '◆ ';
    font-size: 7pt;
}}

/* ── Tabelle ────────────────────────────────────────── */
.chapter-body table {{
    width: 100%;
    border-collapse: collapse;
    margin: 3mm 0;
    font-size: 8.5pt;
    break-inside: avoid;
}}

.chapter-body table thead tr {{
    background: var(--midnight);
    color: var(--white);
}}

.chapter-body table thead th {{
    font-family: 'Cinzel', serif;
    font-size: 7.5pt;
    font-weight: 700;
    color: var(--white);
    padding: 1.8mm 2mm;
    text-align: center;
    letter-spacing: 0.04em;
    border: 0.5pt solid #2a2a4a;
}}

.chapter-body table tbody tr:nth-child(even) {{
    background: var(--parchment);
}}

.chapter-body table tbody tr:nth-child(odd) {{
    background: var(--white);
}}

.chapter-body table td {{
    padding: 1.5mm 2mm;
    border: 0.3pt solid #cccccc;
    vertical-align: top;
    line-height: 1.35;
}}

.chapter-body table tbody tr:hover {{
    background: var(--parchment2);
}}

/* ── Tabelle WIDE: escono dal flusso a 2 colonne ─── */
.table-wide {{
    column-span: all;
    margin: 4mm 0;
    break-inside: avoid;
}}

.table-wide table {{
    font-size: 8pt;
}}

/* ── Callout boxes ──────────────────────────────────── */
.box {{
    border-radius: 0;
    padding: 3mm 3.5mm;
    margin: 3mm 0;
    break-inside: avoid;
    font-size: 8.5pt;
    line-height: 1.4;
}}

.box .box-title {{
    font-family: 'Cinzel', serif;
    font-size: 8pt;
    font-weight: 700;
    margin-bottom: 1.5mm;
    letter-spacing: 0.03em;
}}

.box p {{
    text-indent: 0;
    margin-bottom: 1mm;
    font-size: 8.5pt;
}}

.box p:last-child {{ margin-bottom: 0; }}

.box ul, .box ol {{
    margin: 1mm 0 1mm 3mm;
    padding-left: 2mm;
}}

.box li {{ font-size: 8.5pt; margin-bottom: 0.8mm; }}

/* Box variants */
.box-warn    {{ background: var(--box-warn);    border-left: 2.5pt solid var(--accent-warn);    border-top: 0.3pt solid var(--accent-warn);    border-bottom: 0.3pt solid var(--accent-warn); border-right: 0.3pt solid var(--accent-warn); }}
.box-info    {{ background: var(--box-info);    border-left: 2.5pt solid var(--accent-info);    border-top: 0.3pt solid var(--accent-info);    border-bottom: 0.3pt solid var(--accent-info); border-right: 0.3pt solid var(--accent-info); }}
.box-tip     {{ background: var(--box-tip);     border-left: 2.5pt solid var(--accent-tip);     border-top: 0.3pt solid var(--accent-tip);     border-bottom: 0.3pt solid var(--accent-tip);  border-right: 0.3pt solid var(--accent-tip); }}
.box-danger  {{ background: var(--box-danger);  border-left: 2.5pt solid var(--accent-danger);  border-top: 0.3pt solid var(--accent-danger);  border-bottom: 0.3pt solid var(--accent-danger); border-right: 0.3pt solid var(--accent-danger); }}
.box-example {{ background: var(--box-example); border-left: 2.5pt solid var(--accent-example); border-top: 0.3pt solid var(--accent-example); border-bottom: 0.3pt solid var(--accent-example); border-right: 0.3pt solid var(--accent-example); }}
.box-rule    {{ background: var(--box-rule);    border-left: 2.5pt solid var(--accent-rule);    border-top: 0.3pt solid var(--accent-rule);    border-bottom: 0.3pt solid var(--accent-rule); border-right: 0.3pt solid var(--accent-rule); }}
.box-casata_avalon  {{ background: var(--box-avalon);  border-left: 2.5pt solid var(--accent-avalon);  border-top: 0.3pt solid var(--accent-avalon);  border-bottom: 0.3pt solid var(--accent-avalon);  border-right: 0.3pt solid var(--accent-avalon); }}
.box-casata_umbra   {{ background: var(--box-umbra);   border-left: 2.5pt solid var(--accent-umbra);   border-top: 0.3pt solid var(--accent-umbra);   border-bottom: 0.3pt solid var(--accent-umbra);   border-right: 0.3pt solid var(--accent-umbra); }}
.box-casata_ife     {{ background: var(--box-ife);     border-left: 2.5pt solid var(--accent-ife);     border-top: 0.3pt solid var(--accent-ife);     border-bottom: 0.3pt solid var(--accent-ife);     border-right: 0.3pt solid var(--accent-ife); }}
.box-casata_mictlan {{ background: var(--box-mictlan); border-left: 2.5pt solid var(--accent-mictlan); border-top: 0.3pt solid var(--accent-mictlan); border-bottom: var(--accent-mictlan); border-right: 0.3pt solid var(--accent-mictlan); }}

.box-warn    .box-title {{ color: var(--accent-warn); }}
.box-info    .box-title {{ color: var(--accent-info); }}
.box-tip     .box-title {{ color: var(--accent-tip); }}
.box-danger  .box-title {{ color: var(--accent-danger); }}
.box-example .box-title {{ color: var(--accent-example); }}
.box-rule    .box-title {{ color: var(--accent-rule); }}
.box-casata_avalon  .box-title {{ color: var(--accent-avalon); }}
.box-casata_umbra   .box-title {{ color: var(--accent-umbra); }}
.box-casata_ife     .box-title {{ color: var(--accent-ife); }}
.box-casata_mictlan .box-title {{ color: var(--accent-mictlan); }}

/* ── Stat block bestiario ───────────────────────────── */
.stat-block {{
    background: var(--midnight);
    color: var(--white);
    padding: 3mm 3.5mm;
    margin: 3mm 0;
    break-inside: avoid;
    font-size: 8.5pt;
}}

.stat-block .stat-name {{
    font-family: 'Cinzel', serif;
    font-size: 10pt;
    font-weight: 700;
    color: var(--white);
    border-bottom: 0.5pt solid var(--gold);
    padding-bottom: 1.5mm;
    margin-bottom: 2mm;
    letter-spacing: 0.05em;
}}

.stat-block .stat-name .stat-icon {{
    color: var(--gold);
    margin-right: 1mm;
}}

.stat-block table {{
    background: transparent;
    margin: 1.5mm 0;
}}

.stat-block table thead tr {{
    background: rgba(255,255,255,0.1);
}}

.stat-block table thead th {{
    color: var(--gold-light);
    border-color: rgba(255,255,255,0.2);
    font-size: 7pt;
}}

.stat-block table tbody tr:nth-child(even) {{
    background: rgba(255,255,255,0.05);
}}
.stat-block table tbody tr:nth-child(odd) {{
    background: transparent;
}}
.stat-block table td {{
    color: var(--white);
    border-color: rgba(255,255,255,0.15);
    font-size: 8pt;
}}

.stat-block p {{
    color: #cccccc;
    font-size: 8.5pt;
    margin-bottom: 1mm;
    text-indent: 0;
}}

/* ── Citazione ──────────────────────────────────────── */
.quote-block {{
    border-left: 2pt solid var(--gold);
    padding: 2mm 3mm;
    margin: 3mm 2mm;
    font-style: italic;
    color: var(--gray-dark);
    font-size: 9pt;
    line-height: 1.5;
    break-inside: avoid;
}}

/* ── Separatore ─────────────────────────────────────── */
.chapter-body hr {{
    border: none;
    border-top: 0.5pt solid var(--crimson);
    margin: 4mm 0;
    opacity: 0.4;
}}

/* ── Code inline ────────────────────────────────────── */
code {{
    font-family: 'DejaVu Sans Mono', monospace;
    font-size: 7.5pt;
    background: var(--gray-light);
    padding: 0 1mm;
    border-radius: 1pt;
    color: var(--crimson);
}}

/* ── Strong / Em ────────────────────────────────────── */
strong {{ font-weight: 700; color: var(--ink); }}
em     {{ font-style: italic; color: var(--ink-light); }}

/* ── Page break utilities ───────────────────────────── */
.page-break  {{ page-break-after: always; }}
.col-break   {{ break-after: column; }}
.no-break    {{ break-inside: avoid; }}
"""


# ═══════════════════════════════════════════════════════════
# MARKDOWN PARSER con estensioni custom
# ═══════════════════════════════════════════════════════════
BOX_ICONS = {
    'warn':           '⚠️',
    'info':           '💡',
    'tip':            '✅',
    'danger':         '🔴',
    'example':        '📖',
    'rule':           '📏',
    'casata_avalon':  '☀️',
    'casata_umbra':   '🌑',
    'casata_ife':     '🌿',
    'casata_mictlan': '💀',
}


def parse_frontmatter(text: str):
    """Estrae frontmatter YAML e corpo Markdown."""
    if not text.startswith('---\n'):
        return {}, text
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}, text
    fm_raw = text[4:end]
    body   = text[end+5:]
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except Exception:
        fm = {}
    return fm, body


def md_to_html_body(text: str) -> str:
    """
    Converte Markdown con estensioni custom in HTML.
    Gestisce: :::box, :::table-wide, :::quote, :::stat-block, [pagebreak], [colbreak]
    """
    # ── Pre-processa estensioni custom prima del parsing MD ──

    # [pagebreak] e [colbreak]
    text = re.sub(r'^\[pagebreak\]\s*$',
                  '<div class="page-break"></div>', text, flags=re.MULTILINE)
    text = re.sub(r'^\[colbreak\]\s*$',
                  '<div class="col-break"></div>',  text, flags=re.MULTILINE)

    # :::stat-block[Nome]...::: → trasformiamo in div speciale
    def replace_stat_block(m):
        name     = m.group(1).strip()
        content  = m.group(2).strip()
        inner_md = md_to_html_body(content)
        return (f'<div class="stat-block no-break">'
                f'<div class="stat-name"><span class="stat-icon">⚔️</span>{name}</div>'
                f'{inner_md}</div>')
    text = re.sub(
        r':::stat-block\[([^\]]+)\]\n([\s\S]*?):::',
        replace_stat_block, text)

    # :::table-wide...::: → div con class table-wide
    def replace_table_wide(m):
        inner_md = md_to_html_body(m.group(1).strip())
        return f'<div class="table-wide">{inner_md}</div>'
    text = re.sub(r':::table-wide\n([\s\S]*?):::', replace_table_wide, text)

    # :::quote...::: → blockquote styled
    def replace_quote(m):
        inner_md = md_to_html_body(m.group(1).strip())
        return f'<div class="quote-block">{inner_md}</div>'
    text = re.sub(r':::quote\n([\s\S]*?):::', replace_quote, text)

    # :::box[Titolo]{type=xxx}...::: → callout box
    def replace_box(m):
        title    = m.group(1).strip()
        btype    = m.group(2).strip() if m.group(2) else 'info'
        content  = m.group(3).strip()
        icon     = BOX_ICONS.get(btype, '💡')
        inner_md = md_to_html_body(content)
        title_html = (f'<div class="box-title">{icon}&nbsp;{title}</div>'
                      if title else '')
        return (f'<div class="box box-{btype} no-break">'
                f'{title_html}{inner_md}</div>')
    text = re.sub(
        r':::box\[([^\]]*)\](?:\{type=([^}]*)\})?\n([\s\S]*?):::',
        replace_box, text)

    # ── Ora parsing Markdown standard ──
    md = MarkdownIt('commonmark', {'typographer': True}).enable('table')
    html = md.render(text)

    # ── Post-processa: sistema i tag headings per WeasyPrint ──
    # h1 non esiste nel corpo (è il chapter-title) — promuovi h2→h2, h3→h3, h4→h4
    return html


# ═══════════════════════════════════════════════════════════
# HTML ASSEMBLER
# ═══════════════════════════════════════════════════════════
def build_toc_html(chapters_meta: list) -> str:
    """Genera il TOC come HTML."""
    entries = []
    current_part = None

    for fm, _ in chapters_meta:
        part = fm.get('part', '')
        chap = fm.get('chapter', '')
        title = fm.get('title', '')

        if part and part != current_part:
            current_part = part
            entries.append(
                f'<div class="toc-entry part">{part}</div>')

        entries.append(
            f'<div class="toc-entry chapter">'
            f'<span class="toc-num">{chap}</span>'
            f'<span class="toc-name">{title}</span>'
            f'<span class="toc-dots"></span>'
            f'<span class="toc-page-num">–</span>'
            f'</div>')

    return (
        '<div class="toc-page">'
        '<div class="toc-title">Indice</div>'
        + ''.join(entries) +
        '</div>')


def build_chapter_html(fm: dict, body_md: str) -> str:
    """Genera HTML completo per un capitolo."""
    title   = fm.get('title', '')
    chapter = fm.get('chapter', '')
    part    = fm.get('part', '')
    epi     = fm.get('epigraph', '')

    part_label = (f'<div class="chapter-part-label">{part}</div>'
                  if part else '')
    chap_label = (f'<div class="chapter-num">Capitolo {chapter}</div>'
                  if chapter else '')
    epi_html   = (f'<div class="chapter-epigraph">«{epi}»</div>'
                  if epi else '')

    header = (
        f'<div class="chapter-header">'
        f'{part_label}'
        f'{chap_label}'
        f'<div class="chapter-title" id="cap{chapter}">{title}</div>'
        f'{epi_html}'
        f'</div>')

    body_html = md_to_html_body(body_md)

    body_section = (
        f'<div class="chapter-body">'
        f'{body_html}'
        f'</div>')

    return header + body_section


def build_cover_html() -> str:
    return (
        '<div class="cover-page">'
        '<div class="cover-ornament">⟡ ⟡ ⟡</div>'
        '<div class="cover-title">Mythic<br>Rings</div>'
        '<div class="cover-subtitle">v3.1 &nbsp;·&nbsp; Guardiani di Milano</div>'
        '<div class="cover-desc">'
        'Un gioco di ruolo di investigazione soprannaturale<br>'
        'nel cuore di Milano — Powered by the Apocalypse'
        '</div>'
        '<div class="cover-ornament" style="margin-top:10mm;">⟡</div>'
        '</div>'
        '<div class="blank-page"></div>')


def build_full_html(chapters_meta: list, css: str) -> str:
    """Assembla il documento HTML completo."""
    parts = [
        '<!DOCTYPE html><html lang="it"><head>',
        '<meta charset="UTF-8">',
        f'<style>{css}</style>',
        '</head><body><div class="document">',
        build_cover_html(),
        build_toc_html(chapters_meta),
    ]

    for fm, body_md in chapters_meta:
        parts.append(build_chapter_html(fm, body_md))

    parts.append('</div></body></html>')
    return '\n'.join(parts)


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════
def render_pdf(chapters_dir: Path, output_dir: Path,
               fonts_dir: Path) -> Path:
    import logging
    logging.getLogger('weasyprint').setLevel(logging.ERROR)
    logging.getLogger('fontTools').setLevel(logging.ERROR)

    print('\n🎨  MYTHIC RINGS v3 — PDF Renderer (WeasyPrint)\n')

    # Carica capitoli
    files = sorted(chapters_dir.glob('*.md'))
    if not files:
        print(f'  Nessun .md trovato in {chapters_dir}')
        sys.exit(1)

    chapters_meta = []
    for f in files:
        raw = f.read_text(encoding='utf-8')
        fm, body = parse_frontmatter(raw)
        if not fm.get('title'):
            fm['title'] = f.stem.replace('_', ' ').title()
        chapters_meta.append((fm, body))
        print(f'  ✓  {f.name:<52s} → {fm.get("title", "?")}')

    print(f'\n  Capitoli: {len(chapters_meta)}')
    print('  Generazione HTML...')

    css      = build_css(fonts_dir)
    full_html = build_full_html(chapters_meta, css)

    # Salva HTML di debug (opzionale)
    debug_html = output_dir / 'Mythic_Rings_v3_debug.html'
    debug_html.write_text(full_html, encoding='utf-8')

    print('  Rendering PDF con WeasyPrint...')

    font_config = FontConfiguration()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / 'Mythic_Rings_v3.pdf'

    doc = HTML(
        string=full_html,
        base_url=str(BASE)
    )

    doc.write_pdf(
        str(out_path),
        font_config=font_config,
        presentational_hints=True,
        uncompressed_pdf=False,
    )

    size_kb = out_path.stat().st_size // 1024
    print(f'\n  ✅  {out_path}  ({size_kb} KB)\n')
    return out_path


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('chapters', nargs='?', default=str(CHAPTERS))
    ap.add_argument('output',   nargs='?', default=str(DIST))
    ap.add_argument('--fonts',  default=str(FONTS))
    args = ap.parse_args()

    render_pdf(
        chapters_dir=Path(args.chapters),
        output_dir=Path(args.output),
        fonts_dir=Path(args.fonts),
    )
