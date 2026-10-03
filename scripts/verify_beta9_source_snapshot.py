#!/usr/bin/env python3
"""Verify the immutable Mythic Rings 0.9.3-beta.9 source snapshot."""
from pathlib import Path
import base64
import hashlib
import zipfile
import sys

ROOT = Path(__file__).resolve().parents[1]
REL = ROOT / "sources" / "releases" / "0.9.3-beta.9"
PARTS = REL / "snapshot_parts"
EXPECTED_ZIP_SHA256 = "ef9ddd10169c44892b86dca54c9b9a0e5a3f52e8e710ff173394e5acf4781ad1"
EXPECTED_ZIP_BYTES = 256120
EXPECTED_PARTS = 18
EXPECTED_FILES = 48
EXPECTED_CHAPTERS = 33

errors = []

chapters = sorted((REL / "chapters").glob("*.md"))
if len(chapters) != EXPECTED_CHAPTERS:
    errors.append(f"chapters: {len(chapters)} != {EXPECTED_CHAPTERS}")

pipeline = sorted((REL / "pipeline").glob("*.py"))
if len(pipeline) != 8:
    errors.append(f"pipeline scripts: {len(pipeline)} != 8")

parts = sorted(PARTS.glob("part-*.b64"))
if len(parts) != EXPECTED_PARTS:
    errors.append(f"snapshot parts: {len(parts)} != {EXPECTED_PARTS}")

if not errors:
    encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    try:
        data = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        errors.append(f"base64 decode: {exc}")
        data = b""

    if data:
        actual = hashlib.sha256(data).hexdigest()
        if actual != EXPECTED_ZIP_SHA256:
            errors.append(f"ZIP SHA-256: {actual} != {EXPECTED_ZIP_SHA256}")
        if len(data) != EXPECTED_ZIP_BYTES:
            errors.append(f"ZIP bytes: {len(data)} != {EXPECTED_ZIP_BYTES}")

        try:
            import io
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                bad = zf.testzip()
                if bad:
                    errors.append(f"ZIP corrupt member: {bad}")
                files = [x for x in zf.namelist() if not x.endswith("/")]
                if len(files) != EXPECTED_FILES:
                    errors.append(f"ZIP files: {len(files)} != {EXPECTED_FILES}")
        except Exception as exc:
            errors.append(f"ZIP validation: {exc}")

required = [
    REL / "README.md",
    REL / "SOURCE_MANIFEST.yml",
    REL / "SHA256SUMS.txt",
    REL / "book.yml",
    REL / "reference" / "APPENDICES_A-D_TEXT.md",
    REL / "reconstruct_source_snapshot.py",
]
for p in required:
    if not p.is_file():
        errors.append(f"missing: {p.relative_to(ROOT)}")

if errors:
    print("FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("PASS")
print(f"chapters={len(chapters)}")
print(f"pipeline_scripts={len(pipeline)}")
print(f"snapshot_parts={len(parts)}")
print(f"snapshot_zip_sha256={EXPECTED_ZIP_SHA256}")
print(f"snapshot_zip_bytes={EXPECTED_ZIP_BYTES}")
print(f"snapshot_files={EXPECTED_FILES}")
