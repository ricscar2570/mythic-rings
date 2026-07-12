#!/usr/bin/env python3
from __future__ import annotations
import sys
import shutil
from pathlib import Path
import yaml

try:
    import fitz
except ImportError:
    print('PyMuPDF non disponibile: impossibile aggiungere metadati e segnalibri.', file=sys.stderr)
    raise SystemExit(1)

root = Path(__file__).resolve().parents[1]
meta = yaml.safe_load((root / 'book.yml').read_text(encoding='utf-8'))
pdf_path = Path(sys.argv[1])
if not pdf_path.exists() or pdf_path.stat().st_size == 0:
    print(f'PDF assente o vuoto: {pdf_path}', file=sys.stderr)
    raise SystemExit(1)

# Lavora su una copia: l'artefatto originale resta valido fino al commit atomico.
tmp = pdf_path.with_suffix('.postprocess.pdf')
if tmp.exists():
    tmp.unlink()
shutil.copy2(pdf_path, tmp)
doc = fitz.open(tmp)
metadata = doc.metadata or {}
metadata.update({
    'title': f"{meta['title']} - {meta['subtitle']}",
    'author': meta['author'],
    'subject': meta['system_description'],
    'keywords': 'gioco di ruolo, urban fantasy, Milano, 2d6',
    'creator': f"Mythic Rings build {meta['version']}",
    'producer': 'LibreOffice + PyMuPDF',
})
doc.set_metadata(metadata)

# Estrazione singola: il precedente ciclo capitoli x pagine rendeva il
# post-processing superlineare sui manuali lunghi.
page_texts = [page.get_text('text') for page in doc]
page_lower = [text.casefold() for text in page_texts]

toc = [[1, f"{meta['title']} - {meta['edition']}", 1]]
used_pages: set[int] = set()
for rel in meta['chapters']:
    raw = (root / rel).read_text(encoding='utf-8')
    if not raw.startswith('---'):
        continue
    _, fm_text, _ = raw.split('---', 2)
    fm = yaml.safe_load(fm_text)
    title = str(fm.get('title', '')).strip()
    chapter = fm.get('chapter')
    title_key = title.casefold()
    marker_key = f"capitolo {chapter}".casefold()
    page_found = None

    # Prima cerca marker e titolo sulla stessa pagina, evitando l'indice.
    for idx, text in enumerate(page_lower[1:], start=1):
        if marker_key in text and title_key in text:
            page_found = idx + 1
            break
    # Fallback sul titolo, sempre dopo le prime pagine.
    if page_found is None:
        for idx, text in enumerate(page_lower[2:], start=2):
            if title_key and title_key in text:
                page_found = idx + 1
                break
    if page_found and page_found not in used_pages:
        toc.append([1, f"{chapter}. {title}", page_found])
        used_pages.add(page_found)

# Back matter.
for label in ('Colophon', 'Crediti e Ringraziamenti'):
    key = label.casefold()
    for idx in range(max(0, len(doc) - 12), len(doc)):
        if key in page_lower[idx]:
            toc.append([1, label, idx + 1])
            break

if len(toc) > 1:
    doc.set_toc(toc)

# Metadati e outline sono modifiche adatte al salvataggio incrementale:
# evita la riscrittura completa di centinaia di pagine e il blocco
# intermittente osservato con garbage=4/clean=True.
doc.saveIncr()
doc.close()
if not tmp.exists() or tmp.stat().st_size == 0:
    print('Salvataggio PDF post-processato fallito.', file=sys.stderr)
    raise SystemExit(1)
# Verifica che il PDF temporaneo sia riapribile prima di sostituire l'originale.
check = fitz.open(tmp)
if check.page_count == 0:
    check.close()
    print('PDF post-processato privo di pagine.', file=sys.stderr)
    raise SystemExit(1)
check.close()
tmp.replace(pdf_path)
print(f"Metadati impostati; segnalibri creati: {len(toc)}")
