#!/usr/bin/env python3
"""
MYTHIC RINGS v3 — Chapter Cleaner v2
Corregge tutti gli artefatti di conversione nei 33 file .md
"""
import re, os, glob, sys

DRY_RUN  = "--dry-run"  in sys.argv
VERBOSE  = "--verbose"  in sys.argv
CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chapters")
SEP_RE = re.compile(r"^\s*-+(\s+-+)+\s*$")


def parse_rst_grid_table(block):
    lines = block.strip().split("\n")
    rows_raw, current_cells, header_done = [], None, False
    for line in lines:
        ls = line.strip()
        if re.match(r"^\+[-=+]+\+\s*$", ls):
            if current_cells is not None:
                rows_raw.append(("header" if not header_done else "body", current_cells))
                current_cells = None
            if "=" in ls:
                header_done = True
            continue
        if ls.startswith("|"):
            cells = [c.strip() for c in ls.split("|")[1:-1]]
            if current_cells is None:
                current_cells = cells
            else:
                for i, cell in enumerate(cells):
                    cell = cell.strip()
                    if i < len(current_cells) and cell:
                        current_cells[i] = (current_cells[i] + " " + cell).strip() if current_cells[i] else cell
    if current_cells is not None:
        rows_raw.append(("body", current_cells))
    if not rows_raw:
        return None
    headers, body_rows = [], []
    for kind, cells in rows_raw:
        clean = [re.sub(r"\*\*", "", c).strip() for c in cells]
        (headers if kind == "header" else body_rows).append(clean)
    if not headers:
        if body_rows:
            headers = body_rows.pop(0)
        else:
            return None
    n = len(headers)
    def mdr(cells):
        p = (list(cells)+[" "]*n)[:n]
        return "| "+" | ".join((c or " ").replace("|","\\|") for c in p)+" |"
    out = [mdr(headers), "|"+"| ".join(["---"]*n)+"|"]
    out += [mdr(r) for r in body_rows if any(r)]
    return "\n".join(out)


def _find_pos(line, n_cols):
    positions, offset = [], 0
    for part in re.split(r"  +", line):
        ps = part.strip()
        if ps:
            idx = line.find(ps, offset)
            if idx >= 0:
                positions.append(idx)
                offset = idx + len(ps)
    return positions[:n_cols] if len(positions) >= 2 else None


def parse_pandoc_simple_table(block):
    lines = block.split("\n")
    seps  = [(i, l) for i, l in enumerate(lines) if SEP_RE.match(l.rstrip())]
    if not seps:
        return None
    longest_sep = max(seps, key=lambda x: x[1].count("-"))[1]
    n_cols = len(re.findall(r"-+", longest_sep))
    if n_cols < 2:
        return None
    col_pos = [m.start() for m in re.finditer(r"-+", longest_sep)][:n_cols]
    body    = lines[seps[0][0]+1 : seps[-1][0]] if len(seps) >= 2 else lines[seps[0][0]+1:]
    non_empty = [l for l in body if l.strip()]
    calibrated, first_blank = False, False
    for line in body:
        if not line.strip():
            first_blank = True
            continue
        if first_blank and not calibrated:
            found = _find_pos(line, n_cols)
            if found:
                col_pos = found
                calibrated = True
                break
    if not calibrated and len(non_empty) >= 2:
        found = _find_pos(non_empty[1], n_cols)
        if found:
            col_pos = found
            calibrated = True
    while len(col_pos) < n_cols:
        col_pos.append(col_pos[-1] + 12)
    def split_at(line):
        cells = []
        for i, s in enumerate(col_pos):
            e = col_pos[i+1] if i+1 < n_cols else len(line)+200
            cell = line[s:min(e, len(line))].strip() if len(line) > s else ""
            cells.append(re.sub(r"\*\*", "", cell).strip())
        return cells
    def col0_filled(line):
        if not line.strip(): return False
        s = col_pos[0]; e = col_pos[1] if n_cols > 1 else s+15
        return bool(line[s:min(e,len(line))].strip()) if len(line) > s else False
    blank_count = sum(1 for l in body if not l.strip())
    if blank_count >= 2:
        records, cur = [], []
        for l in body:
            if not l.strip():
                if cur: records.append(cur); cur=[]
            else: cur.append(l)
        if cur: records.append(cur)
    else:
        records, cur = [], []
        for l in body:
            if not l.strip():
                if cur: records.append(cur); cur=[]
            elif col0_filled(l):
                if cur: records.append(cur)
                cur=[l]
            else:
                if cur: cur.append(l)
        if cur: records.append(cur)
    if not records: return None
    def merge(rec):
        cells = [""]*n_cols
        for line in rec:
            for i,c in enumerate(split_at(line)[:n_cols]):
                if c: cells[i]=(cells[i]+" "+c).strip() if cells[i] else c
        return cells
    header = merge(records[0])
    rows   = [merge(r) for r in records[1:] if any(merge(r))]
    def mdr(cells):
        s = [(c or " ").replace("|","\\|") for c in (cells+[" "]*n_cols)[:n_cols]]
        return "| "+" | ".join(s)+" |"
    out = [mdr(header), "|"+"| ".join(["---"]*n_cols)+"|"]
    out += [mdr(r) for r in rows]
    return "\n".join(out)


def fix_emdash(text):
    text = re.sub(r"(?<!-) --- (?!-)", " - ", text)
    text = re.sub(r"(?<!-) -- (?!-)", " - ", text)
    return text.replace("\u2014"," - ").replace("\u2013","-")

def fix_bold_closing(text):
    text = re.sub(r"^(Parte [IVX]+)\*\*", r"\1", text, flags=re.MULTILINE)
    text = re.sub(r"^(#{1,4} .+?)\*\*\s*$", r"\1", text, flags=re.MULTILINE)
    return text

def fix_indented_headings(text):
    def repl(m):
        title = m.group(1).strip()
        clean = re.sub(r"^[\u2600-\u27ff\U0001F000-\U0001FFFF ]+", "", title).strip()
        level = "##" if (clean.isupper() or len(clean) < 35) else "###"
        return f"\n{level} {title}\n"
    return re.sub(r"^\s{2,}\*\*([^*\n]{2,80})\*\*\s*$", repl, text, flags=re.MULTILINE)

def fix_dividers(text):
    return re.sub(r"^\s{2,}-{5,}\s*$\n?", "", text, flags=re.MULTILINE)

def fix_single_col_tables(text):
    pat = re.compile(r"\n(\|[^\n|]+\|\n\|---\|\n(?:\|[^\n|]+\|\n)+)", re.MULTILINE)
    def repl(m):
        rows = re.findall(r"\|([^|\n]+)\|", m.group(1))
        rows = [r.strip() for r in rows if r.strip() and r.strip()!="---"]
        if not rows: return m.group(0)
        return "\n\n:::quote\n" + "\n".join(rows) + "\n:::\n\n"
    return pat.sub(repl, text)

def fix_tables(text):
    rst_pat = re.compile(r"(\+[-=+]+\+[\s\S]*?\n\+[-=+]+\+\s*\n)", re.MULTILINE)
    def repl_rst(m):
        r = parse_rst_grid_table(m.group(0))
        return ("\n"+r+"\n") if r else m.group(0)
    text = rst_pat.sub(repl_rst, text)
    
    pandoc_pat = re.compile(
        r"((?:[ \t]+-+[ \t]*)+[ \t]*-+[ \t]*\n"
        r"(?:[ \t]+\S[^\n]*\n)*"
        r"(?:\n(?:[ \t]+\S[^\n]*\n)*)*"
        r"(?:(?:[ \t]+-+[ \t]*)+[ \t]*-+[ \t]*\n)?)",
        re.MULTILINE
    )
    def repl_pandoc(m):
        r = parse_pandoc_simple_table(m.group(0))
        return ("\n"+r+"\n") if r else m.group(0)
    text = pandoc_pat.sub(repl_pandoc, text)
    return text

def fix_trailing(text):
    text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"

def process_file(fpath):
    fname = os.path.basename(fpath)
    original = open(fpath, encoding="utf-8").read()
    parts = original.split("---\n", 2)
    if len(parts) < 3:
        return 0
    fm_raw = "---\n" + parts[1] + "---\n"
    body, orig = parts[2], parts[2]
    body = fix_tables(body)
    body = fix_dividers(body)
    body = fix_indented_headings(body)
    body = fix_bold_closing(body)
    body = fix_emdash(body)
    body = fix_single_col_tables(body)
    body = fix_trailing(body)
    if body == orig:
        if VERBOSE: print(f"  nessuna modifica: {fname}")
        return 0
    changes = sum(1 for a,b in zip(orig.splitlines(), body.splitlines()) if a!=b)
    changes += abs(len(orig.splitlines())-len(body.splitlines()))
    if not DRY_RUN:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(fm_raw + "\n" + body)
    print(f"  {'[DRY]' if DRY_RUN else chr(10003)}  {fname:<52s} ({changes} righe)")
    return changes

files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "*.md")))
if not files:
    print(f"Nessun file trovato in {CHAPTERS_DIR}"); sys.exit(1)
print(f"\n Mythic Rings — Chapter Cleaner v2 ({len(files)} file)\n")
total = sum(process_file(f) for f in files)
print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Righe modificate: {total}\n")
