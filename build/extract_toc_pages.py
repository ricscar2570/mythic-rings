#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
import fitz
import yaml

root = Path(__file__).resolve().parents[1]
meta = yaml.safe_load((root / 'book.yml').read_text(encoding='utf-8'))
pdf = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else root / 'dist/toc-pages.json'

doc = fitz.open(pdf)
page_texts = [p.get_text('text') for p in doc]
result = {}
missing = []
for rel in meta['chapters']:
    raw = (root / rel).read_text(encoding='utf-8')
    fm = yaml.safe_load(raw.split('---',2)[1])
    number = str(fm['chapter'])
    title = str(fm['title'])
    marker = f'Capitolo {number}'
    found = None
    for idx, text in enumerate(page_texts):
        if idx < 1:
            continue
        if marker.lower() in text.lower() and title.lower() in text.lower():
            found = idx + 1
            break
    if found is None:
        # Fallback: exact title after the TOC pages.
        for idx, text in enumerate(page_texts[2:], start=2):
            if title.lower() in text.lower():
                found = idx + 1
                break
    if found is None:
        missing.append(f'{number}: {title}')
    else:
        result[number] = found
        result[title] = found
out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Pagine indice estratte: {len(result)//2}/{len(meta["chapters"])}')
if missing:
    print('Non trovati: ' + '; '.join(missing), file=sys.stderr)
    sys.exit(2)
