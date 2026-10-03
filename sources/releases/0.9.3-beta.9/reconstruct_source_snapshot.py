#!/usr/bin/env python3
from pathlib import Path
import base64
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parent
PART_DIR = ROOT / "snapshot_parts"
OUTPUT = ROOT / "Mythic_Rings_0.9.3-beta.9_SOURCE_SNAPSHOT.zip"
EXPECTED = "ef9ddd10169c44892b86dca54c9b9a0e5a3f52e8e710ff173394e5acf4781ad1"

parts = sorted(PART_DIR.glob("part-*.b64"))
if len(parts) != 18:
    raise SystemExit(f"Expected 18 parts, found {len(parts)}")

encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
data = base64.b64decode(encoded, validate=True)
actual = hashlib.sha256(data).hexdigest()
if actual != EXPECTED:
    raise SystemExit(f"SHA-256 mismatch: {actual} != {EXPECTED}")

OUTPUT.write_bytes(data)
print(f"Wrote {OUTPUT} ({len(data)} bytes)")
print(f"SHA-256 {actual}")

with zipfile.ZipFile(OUTPUT) as zf:
    bad = zf.testzip()
    if bad:
        raise SystemExit(f"ZIP integrity failure at {bad}")
    names = zf.namelist()
    print(f"ZIP OK: {len(names)} entries")

print("To extract:")
print(f"  python -m zipfile -e {OUTPUT.name} ./reconstructed")
