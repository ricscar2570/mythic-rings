#!/usr/bin/env python3
from __future__ import annotations
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable

import yaml
from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "products"
REF = ROOT / "build" / "product-reference.docx"
META = yaml.safe_load((ROOT / "book.yml").read_text(encoding="utf-8"))

PRODUCTS = [
    {
        "source": ROOT / "products/quickstart/Mythic_Rings_Quickstart.md",
        "basename": "Mythic_Rings_Quickstart_beta1",
        "toc": False,
        "title": "Mythic Rings — Quickstart",
    },
    {
        "source": ROOT / "products/player-kit/Mythic_Rings_Kit_del_Giocatore.md",
        "basename": "Mythic_Rings_Kit_del_Giocatore_beta1",
        "toc": False,
        "title": "Mythic Rings — Kit del Giocatore",
    },
    {
        "source": ROOT / "products/adventure/Mythic_Rings_Notte_al_Monumentale.md",
        "basename": "Mythic_Rings_Notte_al_Monumentale_beta1",
        "toc": False,
        "title": "Mythic Rings — Notte al Monumentale",
    },
]


def set_cell_margins(cell, top=80, start=90, bottom=80, end=90):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tcMar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def add_page_field(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr, fld_char2])


def style_font(style, name: str, size: float, *, bold=False, italic=False, color=None):
    style.font.name = name
    style._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    if color:
        style.font.color.rgb = RGBColor(*color)


def create_reference_docx(path: Path) -> None:
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(14.8)
    sec.page_height = Cm(21.0)
    sec.top_margin = Cm(1.5)
    sec.bottom_margin = Cm(1.5)
    sec.left_margin = Cm(1.6)
    sec.right_margin = Cm(1.4)
    sec.gutter = Cm(0.3)
    sec.start_type = WD_SECTION_START.NEW_PAGE

    styles = doc.styles
    normal = styles["Normal"]
    style_font(normal, "EB Garamond", 10.2, color=(35, 35, 38))
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.08

    for name, size, color, before, after in [
        ("Title", 28, (116, 26, 38), 0, 14),
        ("Subtitle", 15, (164, 126, 56), 0, 18),
        ("Heading 1", 18, (116, 26, 38), 16, 8),
        ("Heading 2", 13, (30, 42, 60), 12, 5),
        ("Heading 3", 11, (116, 26, 38), 9, 4),
        ("Heading 4", 10.5, (50, 50, 55), 7, 3),
    ]:
        st = styles[name]
        style_font(st, "Cinzel" if name != "Subtitle" else "EB Garamond", size,
                   bold=name != "Subtitle", italic=name == "Subtitle", color=color)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    for name in ["Header", "Footer"]:
        style_font(styles[name], "EB Garamond", 8.5, color=(100, 100, 105))

    # Quote style
    if "Block Text" in styles:
        bt = styles["Block Text"]
        style_font(bt, "EB Garamond", 9.8, italic=True, color=(75, 75, 80))
        bt.paragraph_format.left_indent = Cm(0.7)
        bt.paragraph_format.right_indent = Cm(0.7)

    # Code-like style if present
    if "Verbatim Char" in styles:
        style_font(styles["Verbatim Char"], "Liberation Mono", 8.5)

    # Add a document title placeholder so footer and styles are retained.
    doc.add_paragraph("Mythic Rings", style="Title")
    footer = sec.footer.paragraphs[0]
    add_page_field(footer)

    doc.save(path)



def _set_table_fixed_width(table, total_twips: int = 6200) -> None:
    """Force an inline table with explicit grid and cell widths for LO."""
    tbl_pr = table._tbl.tblPr
    for node in list(tbl_pr):
        if node.tag == qn("w:tblpPr"):
            tbl_pr.remove(node)

    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.insert(0, tbl_w)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), str(total_twips))

    jc = tbl_pr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        tbl_pr.append(jc)
    jc.set(qn("w:val"), "center")

    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")

    cols = len(table.columns)
    if cols == 2:
        ratios = [0.34, 0.66]
    elif cols == 3:
        ratios = [0.25, 0.36, 0.39]
    elif cols == 5:
        ratios = [0.20] * 5
    elif cols == 6:
        ratios = [0.22, 0.10, 0.10, 0.15, 0.13, 0.30]
    else:
        ratios = [1 / cols] * cols
    widths = [round(total_twips * r) for r in ratios]
    widths[-1] += total_twips - sum(widths)

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.insert(0, tc_w)
            tc_w.set(qn("w:type"), "dxa")
            tc_w.set(qn("w:w"), str(widths[min(idx, len(widths)-1)]))

def _repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:tblHeader")) is None:
        header = OxmlElement("w:tblHeader")
        header.set(qn("w:val"), "true")
        tr_pr.append(header)


def postprocess_product_docx(path: Path) -> None:
    """Rebuild Pandoc tables as native python-docx tables.

    LibreOffice can misrender Pandoc-generated tables in compact A5 files,
    overlaying borders over subsequent paragraphs even when the OOXML does not
    contain floating-table properties. Rebuilding the table nodes produces a
    stable, inline layout in Word and LibreOffice.
    """
    doc = Document(path)

    for section in doc.sections:
        section.page_width = Cm(14.8)
        section.page_height = Cm(21.0)
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(1.6)
        section.right_margin = Cm(1.4)
        section.gutter = Cm(0.3)

    for style_name in ("Title", "Subtitle", "Heading 1", "Heading 2", "Heading 3", "Heading 4"):
        if style_name in doc.styles:
            fmt = doc.styles[style_name].paragraph_format
            fmt.left_indent = Cm(0)
            fmt.right_indent = Cm(0)
            fmt.first_line_indent = Cm(0)

    for paragraph in doc.paragraphs:
        if paragraph.style and paragraph.style.name.startswith(("Title", "Subtitle", "Heading")):
            paragraph.paragraph_format.left_indent = Cm(0)
            paragraph.paragraph_format.right_indent = Cm(0)
            paragraph.paragraph_format.first_line_indent = Cm(0)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Snapshot before adding replacements: doc.tables is live.
    original_tables = list(doc.tables)
    for old_table in original_tables:
        matrix = [[cell.text for cell in row.cells] for row in old_table.rows]
        if not matrix:
            continue
        col_count = max(len(row) for row in matrix)
        new_table = doc.add_table(rows=len(matrix), cols=col_count)
        new_table.style = "Table Grid"
        new_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        new_table.autofit = True

        for r_idx, values in enumerate(matrix):
            for c_idx in range(col_count):
                cell = new_table.cell(r_idx, c_idx)
                cell.text = values[c_idx] if c_idx < len(values) else ""
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                set_cell_margins(cell, top=55, start=65, bottom=55, end=65)
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_before = Pt(0)
                    paragraph.paragraph_format.space_after = Pt(1)
                    for run in paragraph.runs:
                        run.font.name = "EB Garamond"
                        run._element.rPr.rFonts.set(qn("w:eastAsia"), "EB Garamond")
                        run.font.size = Pt(8.5 if col_count >= 5 else 9.2)
                        if r_idx == 0:
                            run.bold = True
            tr_pr = new_table.rows[r_idx]._tr.get_or_add_trPr()
            if tr_pr.find(qn("w:cantSplit")) is None:
                cant_split = OxmlElement("w:cantSplit")
                cant_split.set(qn("w:val"), "true")
                tr_pr.append(cant_split)
            if r_idx == 0:
                _repeat_header(new_table.rows[0])

        old_xml = old_table._tbl
        old_xml.addprevious(new_table._tbl)
        old_xml.getparent().remove(old_xml)

    if path.name.startswith("Mythic_Rings_Kit_del_Giocatore"):
        for paragraph in doc.paragraphs:
            if paragraph.text.strip() == "Esperienza e avanzamenti":
                paragraph.paragraph_format.page_break_before = True
                break

    # Remove empty paragraphs left at the end by the temporary appended tables.
    body = doc._body._element
    for paragraph in list(body.findall(qn("w:p"))):
        texts = paragraph.findall('.//' + qn("w:t"))
        if not texts and paragraph is not body[-1]:
            # Preserve explicit page breaks and styled spacing paragraphs.
            if paragraph.find('.//' + qn("w:br")) is None and paragraph.find(qn("w:pPr")) is None:
                body.remove(paragraph)

    doc.save(path)

def run(cmd: list[str], *, cwd: Path = ROOT, timeout: int = 300) -> None:
    """Execute a build command in an isolated process group.

    Output is redirected to a temporary file rather than a PIPE. LibreOffice
    helper processes may inherit pipe descriptors; in that case ``communicate``
    can wait forever even after the launcher has been terminated. A regular
    file plus bounded ``wait`` calls makes success and timeout deterministic.
    """
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as log:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        timed_out = False
        try:
            returncode = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                returncode = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    returncode = proc.wait(timeout=5)
                except subprocess.TimeoutExpired as exc:
                    raise RuntimeError(
                        f"Impossibile terminare il comando scaduto: {' '.join(cmd)}"
                    ) from exc

        log.flush()
        log.seek(0)
        output = log.read()
        if timed_out:
            raise RuntimeError(
                f"Comando scaduto dopo {timeout}s: {' '.join(cmd)}\n{output}"
            )
        if returncode:
            raise RuntimeError(
                f"Comando fallito ({returncode}): {' '.join(cmd)}\n{output}"
            )


def convert_with_libreoffice(docx: Path, pdf: Path, profile: Path, *, timeout: int = 180) -> None:
    """Convert DOCX to PDF without trusting LibreOffice to terminate cleanly.

    On some headless Linux runners LibreOffice finishes writing a valid PDF but
    leaves the launcher alive. We watch the expected output and, once its size
    is stable and PyMuPDF can open every page, terminate the lingering process
    group. A partial or unreadable PDF is never accepted.
    """
    command = [
        "libreoffice", f"-env:UserInstallation={profile.as_uri()}",
        "--headless", "--nologo", "--nodefault", "--nolockcheck",
        "--nofirststartwizard", "--convert-to", "pdf",
        "--outdir", str(DIST), str(docx),
    ]
    if pdf.exists():
        pdf.unlink()

    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as log:
        proc = subprocess.Popen(
            command,
            cwd=ROOT,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        started = time.monotonic()
        stable_size = -1
        stable_checks = 0
        accepted_while_running = False

        while True:
            code = proc.poll()
            if code is not None:
                break

            if pdf.exists() and pdf.stat().st_size > 0:
                size = pdf.stat().st_size
                if size == stable_size:
                    stable_checks += 1
                else:
                    stable_size = size
                    stable_checks = 0

                if stable_checks >= 6:  # about three seconds at 0.5 s intervals
                    try:
                        import fitz
                        probe = fitz.open(pdf)
                        valid = probe.page_count > 0
                        if valid:
                            # Force loading of the last page: truncated xref streams
                            # can otherwise appear openable until page access.
                            probe.load_page(probe.page_count - 1)
                        probe.close()
                    except Exception:
                        valid = False
                    if valid:
                        accepted_while_running = True
                        try:
                            os.killpg(proc.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        try:
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            try:
                                os.killpg(proc.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            proc.wait(timeout=5)
                        break

            if time.monotonic() - started > timeout:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    proc.wait(timeout=5)
                log.flush()
                log.seek(0)
                raise RuntimeError(
                    f"Conversione LibreOffice scaduta dopo {timeout}s: {docx.name}\n{log.read()}"
                )
            time.sleep(0.5)

        log.flush()
        log.seek(0)
        output = log.read()
        code = proc.returncode
        if code not in (0, None) and not accepted_while_running:
            raise RuntimeError(
                f"LibreOffice fallito ({code}) per {docx.name}\n{output}"
            )

    if not pdf.exists() or pdf.stat().st_size == 0:
        raise RuntimeError(f"PDF non prodotto o vuoto per {docx.name}")
    try:
        import fitz
        probe = fitz.open(pdf)
        if probe.page_count == 0:
            raise RuntimeError(f"PDF privo di pagine per {docx.name}")
        probe.load_page(probe.page_count - 1)
        probe.close()
    except Exception as exc:
        raise RuntimeError(f"PDF non valido per {docx.name}: {exc}") from exc


def headings(source: Path) -> list[tuple[int, str]]:
    text = source.read_text(encoding="utf-8")
    # remove YAML frontmatter
    text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.S)
    out = []
    for line in text.splitlines():
        m = re.match(r"^(#)\s+(.+?)\s*$", line)
        if not m:
            continue
        title = re.sub(r"[*_`]", "", m.group(2)).strip()
        out.append((len(m.group(1)), title))
    return out


def add_pdf_metadata_and_toc(pdf: Path, source: Path, title: str) -> None:
    import fitz

    tmp = pdf.with_suffix(".postprocess.pdf")
    if tmp.exists():
        tmp.unlink()
    shutil.copy2(pdf, tmp)
    doc = fitz.open(tmp)
    md = doc.metadata or {}
    md.update({
        "title": title,
        "author": META["author"],
        "subject": "Mythic Rings — materiale di gioco beta",
        "keywords": "Mythic Rings, gioco di ruolo, Milano, quickstart",
        "creator": "Mythic Rings product build",
        "producer": "LibreOffice + PyMuPDF",
    })
    doc.set_metadata(md)

    # Replace any outline generated by LibreOffice with a concise,
    # deterministic product-level outline.
    toc = []
    used_pages = set()
    page_texts = [page.get_text("text") for page in doc]
    for level, heading in headings(source):
        page_no = None
        needles = [heading, heading.replace("—", "-")]
        for i, page_text in enumerate(page_texts):
            if any(needle in page_text for needle in needles):
                page_no = i + 1
                break
        if page_no is not None:
            key = (heading, page_no)
            if key not in used_pages:
                toc.append([1, heading, page_no])
                used_pages.add(key)
    doc.set_toc(toc)

    doc.saveIncr()
    doc.close()
    check = fitz.open(tmp)
    if check.page_count == 0:
        check.close()
        raise RuntimeError(f"PDF post-processato privo di pagine: {pdf.name}")
    check.close()
    tmp.replace(pdf)


def build_product(product: dict) -> None:
    src = product["source"]
    base = product["basename"]
    docx = DIST / f"{base}.docx"
    pdf = DIST / f"{base}.pdf"
    html = DIST / f"{base}.html"

    pandoc = [
        "pandoc", str(src), "--standalone", "--from=gfm", "--reference-doc", str(REF),
        "--metadata", f"title={product['title']}",
        "--metadata", f"author={META['author']}",
        "--output", str(docx),
    ]
    if product["toc"]:
        pandoc.extend(["--toc", "--toc-depth=2"])
    run(pandoc)
    postprocess_product_docx(docx)

    run([
        "pandoc", str(src), "--standalone", "--from=gfm",
        "--metadata", f"title={product['title']}",
        "--metadata", f"author={META['author']}",
        "--output", str(html),
    ])

    # Never let LibreOffice silently leave a stale artifact from an earlier build.
    if pdf.exists():
        pdf.unlink()

    lo_profile = Path(tempfile.mkdtemp(prefix=f"mythic-rings-{base}-", dir="/tmp"))
    try:
        produced = DIST / f"{base}.pdf"
        convert_with_libreoffice(docx, produced, lo_profile, timeout=180)
        add_pdf_metadata_and_toc(produced, src, product["title"])
    finally:
        shutil.rmtree(lo_profile, ignore_errors=True)
    print(f"Creato {docx.name}, {pdf.name}, {html.name}", flush=True)


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    create_reference_docx(REF)
    for product in PRODUCTS:
        build_product(product)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        raise
