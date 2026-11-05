#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import fitz
import yaml

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
BOOK = yaml.safe_load((ROOT / "book.yml").read_text(encoding="utf-8"))
VERSION = str(BOOK["version"])
BASE = ROOT / "archive" / "baselines" / VERSION
SNAPSHOT = BASE / "source_snapshot.tar.gz"
META = BASE / "BASELINE.json"
DIST = ROOT / "dist" / "blind"
PDF = DIST / f"{BOOK['output_basename']}.pdf"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if not parts:
        return False
    if parts[0] in {".git", "archive", "dist", "node_modules"}:
        return False
    if len(parts) >= 2 and parts[0] == "assets" and parts[1] == "fonts":
        return False
    if "__pycache__" in parts or path.suffix == ".pyc":
        return False
    return path.is_file()


files = sorted((p for p in ROOT.rglob("*") if include(p)), key=lambda p: p.relative_to(ROOT).as_posix())
BASE.mkdir(parents=True, exist_ok=True)
with tarfile.open(SNAPSHOT, "w:gz", format=tarfile.PAX_FORMAT) as tar:
    for path in files:
        tar.add(path, arcname=path.relative_to(ROOT).as_posix(), recursive=False)

meta = json.loads(META.read_text(encoding="utf-8")) if META.exists() else {}
meta.update({
    "schema_version": 1,
    "product": "Mythic Rings",
    "product_version": VERSION,
    "baseline_name": "Correzione normativa e sanificazione / Phase 3 Candidate",
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "source_snapshot": {
        "path": SNAPSHOT.relative_to(ROOT).as_posix(),
        "sha256": sha256(SNAPSHOT),
        "file_count": len(files),
        "scope": "Sorgenti e documentazione beta.4.2; esclusi dist, archive, node_modules, font binari e cache.",
    },
})
with fitz.open(PDF) as doc:
    pages = doc.page_count
meta["reference_manual"] = {
    "filename": PDF.name,
    "pages": pages,
    "sha256": sha256(PDF),
    "included_in_repository": True,
    "path": PDF.relative_to(ROOT).as_posix(),
    "note": "Build candidata alla Fase 3 con P0 interni chiusi; G2 umano e G3 restano PENDING.",
}
meta["immutability_policy"] = "La baseline non si modifica. Correzioni successive richiedono una nuova versione e un nuovo snapshot."
META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Baseline finalized: {len(files)} files, {pages} pages")
