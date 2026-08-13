#!/usr/bin/env python3
"""Verifica l'integrità della baseline congelata senza confrontarla con il working tree."""
from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "archive/baselines/0.9.0-beta.2/BASELINE.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    meta = json.loads(META.read_text(encoding="utf-8"))
    rel = Path(meta["source_snapshot"]["path"])
    archive = ROOT / rel
    errors: list[str] = []
    if not archive.is_file() or archive.stat().st_size == 0:
        errors.append(f"snapshot assente o vuoto: {rel}")
    else:
        actual = sha256(archive)
        expected = meta["source_snapshot"]["sha256"]
        if actual != expected:
            errors.append(f"checksum snapshot diverso: {actual} != {expected}")
        try:
            with tarfile.open(archive, "r:gz") as tf:
                members = [m for m in tf.getmembers() if m.isfile()]
                expected_count = meta["source_snapshot"]["file_count"]
                if len(members) != expected_count:
                    errors.append(f"file nello snapshot: {len(members)} != {expected_count}")
                names = {m.name for m in members}
                for required in ["book.yml", "data/canonical_rules.yml", "chapters/05_come_si_gioca.md", "docs/CANONICAL_RULES_SPEC.md"]:
                    if required not in names:
                        errors.append(f"file normativo assente dallo snapshot: {required}")
                book = tf.extractfile("book.yml")
                if book:
                    text = book.read().decode("utf-8", "replace")
                    if "version: 0.9.0-beta.2" not in text:
                        errors.append("book.yml archiviato non identifica 0.9.0-beta.2")
        except Exception as exc:
            errors.append(f"snapshot non apribile: {exc}")

    manual = meta.get("reference_manual", {})
    if manual.get("pages") != 265:
        errors.append("numero pagine manuale baseline inatteso")
    pdfsha = manual.get("sha256", "")
    if not isinstance(pdfsha, str) or len(pdfsha) != 64:
        errors.append("SHA-256 del manuale di riferimento non valido")

    if errors:
        print("Baseline NON valida:")
        for e in errors:
            print(f"- {e}")
        return 1
    print("Baseline verificata:")
    print(f"  versione: {meta['product_version']}")
    print(f"  snapshot: {rel}")
    print(f"  sha256: {meta['source_snapshot']['sha256']}")
    print(f"  file: {meta['source_snapshot']['file_count']}")
    print(f"  manuale riferimento: {manual['pages']} pagine, sha256 {manual['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
