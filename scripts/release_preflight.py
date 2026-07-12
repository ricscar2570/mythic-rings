#!/usr/bin/env python3
"""Preflight tecnico degli artefatti editoriali di Mythic Rings."""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
META = yaml.safe_load((ROOT / "book.yml").read_text(encoding="utf-8"))
DIST = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "dist")
BASE = META["output_basename"]

artifacts = {
    "manual_docx": DIST / f"{BASE}.docx",
    "manual_html": DIST / f"{BASE}.html",
    "manual_pdf": DIST / f"{BASE}.pdf",
    "validation": DIST / "validation-report.json",
    "quickstart_docx": DIST / "products/Mythic_Rings_Quickstart_beta1.docx",
    "quickstart_html": DIST / "products/Mythic_Rings_Quickstart_beta1.html",
    "quickstart_pdf": DIST / "products/Mythic_Rings_Quickstart_beta1.pdf",
    "kit_docx": DIST / "products/Mythic_Rings_Kit_del_Giocatore_beta1.docx",
    "kit_html": DIST / "products/Mythic_Rings_Kit_del_Giocatore_beta1.html",
    "kit_pdf": DIST / "products/Mythic_Rings_Kit_del_Giocatore_beta1.pdf",
    "adventure_docx": DIST / "products/Mythic_Rings_Notte_al_Monumentale_beta1.docx",
    "adventure_html": DIST / "products/Mythic_Rings_Notte_al_Monumentale_beta1.html",
    "adventure_pdf": DIST / "products/Mythic_Rings_Notte_al_Monumentale_beta1.pdf",
}

errors: list[str] = []
warnings: list[str] = []
info: dict[str, object] = {}
texts: dict[str, str] = {}


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = " ".join(
            archive.read(name).decode("utf-8", "ignore")
            for name in archive.namelist()
            if name.startswith("word/") and name.endswith(".xml")
        )
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", " ", xml)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+[’'\-]?\w*\b", text, re.UNICODE))


for key, path in artifacts.items():
    if not path.exists() or path.stat().st_size == 0:
        errors.append(f"Artefatto assente o vuoto: {path.relative_to(DIST)}")
    else:
        info[f"{key}_bytes"] = path.stat().st_size

# Validazione deve essere pulita da errori.
validation_path = artifacts["validation"]
if validation_path.exists():
    try:
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        if validation.get("errors"):
            errors.append(f"Il report di validazione contiene {len(validation['errors'])} errori")
        info["validation_warnings"] = len(validation.get("warnings", []))
    except Exception as exc:
        errors.append(f"Report di validazione illeggibile: {exc}")

# Estrazione contenuto e controlli sui PDF.
try:
    import fitz
except Exception as exc:
    fitz = None
    errors.append(f"PyMuPDF non disponibile: {exc}")

for key, path in artifacts.items():
    if not path.exists() or path.suffix not in {".docx", ".html", ".pdf"}:
        continue
    try:
        if path.suffix == ".docx":
            text = docx_text(path)
        elif path.suffix == ".html":
            html = path.read_text(encoding="utf-8", errors="ignore")
            html = re.sub(r"<(style|script|head)\b[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
            text = re.sub(r"<[^>]+>", " ", html)
        else:
            if fitz is None:
                continue
            document = fitz.open(path)
            text = "\n".join(page.get_text("text") for page in document)
            toc = document.get_toc()
            metadata = document.metadata or {}
            info[f"{key}_pages"] = len(document)
            info[f"{key}_toc_entries"] = len(toc)
            info[f"{key}_title"] = metadata.get("title")
            info[f"{key}_author"] = metadata.get("author")
            if metadata.get("author") != META["author"]:
                warnings.append(f"{path.name}: autore PDF non allineato")
            document.close()
        texts[key] = text
        info[f"{key}_words"] = word_count(text)
    except Exception as exc:
        errors.append(f"{path.name}: impossibile ispezionare il contenuto ({exc})")

# Soglie minime contro artefatti troncati.
minimum_pages = {
    "manual_pdf": 200,
    "quickstart_pdf": 15,
    "kit_pdf": 8,
    "adventure_pdf": 10,
}
for key, minimum in minimum_pages.items():
    pages = info.get(f"{key}_pages", 0)
    if isinstance(pages, int) and pages < minimum:
        errors.append(f"{artifacts[key].name}: soltanto {pages} pagine; attese almeno {minimum}")

manual_toc = info.get("manual_pdf_toc_entries", 0)
if isinstance(manual_toc, int) and manual_toc < len(META["chapters"]):
    errors.append(f"PDF manuale: {manual_toc} segnalibri per {len(META['chapters'])} capitoli")

# Parità approssimativa tra formati: evita versioni vistosamente diverse.
for prefix in ("manual", "quickstart", "kit", "adventure"):
    counts = [
        info.get(f"{prefix}_docx_words", 0),
        info.get(f"{prefix}_html_words", 0),
        info.get(f"{prefix}_pdf_words", 0),
    ]
    counts = [c for c in counts if isinstance(c, int) and c > 0]
    if len(counts) == 3:
        low, high = min(counts), max(counts)
        if high and (high - low) / high > 0.08:
            warnings.append(f"{prefix}: differenza di parole tra formati superiore all'8% ({counts})")

# Contenuti vietati negli artefatti.
for key, text in texts.items():
    for pattern, label in [
        (r"Riccardo\s*\[Cognome\]", "placeholder autore"),
        (r"\[Nome playtester\]", "placeholder playtester"),
        (r"ISBN\s*:?\s*000", "ISBN fittizio"),
        (r"Mythic Rings v3(?:\.|\b)", "versione storica"),
        (r"\b(?:TODO|TBD)\b|DA COMPLETARE", "marcatore incompleto"),
    ]:
        if re.search(pattern, text, re.I):
            errors.append(f"{artifacts[key].name}: {label}")

# Gate esterni: avvisi in beta, errori se qualcuno tenta di dichiarare final.
external_gates = [
    "blind playtest indipendente documentato",
    "developmental e technical editing indipendenti",
    "lettura culturale delle tradizioni rappresentate",
    "verifica legale di nome, licenze, font e contributi",
    "verifica fiscale e dei canali di vendita",
    "validazione commerciale tramite quickstart",
]
info["external_release_gates"] = external_gates
if META.get("release_stage") == "final":
    if META.get("license_status") != "verified":
        errors.append("Release finale vietata: license_status non è verified")
else:
    warnings.append("Artefatti beta: i gate esterni restano obbligatori prima della versione 1.0")

report = {
    "product": META["title"],
    "version": META["version"],
    "stage": META["release_stage"],
    "errors": errors,
    "warnings": warnings,
    "info": info,
}
(DIST / "release-preflight.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
)

for warning in warnings:
    print("AVVISO:", warning)
if errors:
    for error in errors:
        print("ERRORE:", error)
    raise SystemExit(1)
print(
    f"Preflight superato: {len(artifacts)} artefatti; "
    f"manuale {info.get('manual_pdf_pages', '?')} pagine, "
    f"quickstart {info.get('quickstart_pdf_pages', '?')} pagine."
)
