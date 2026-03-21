#!/usr/bin/env python3
"""
MYTHIC RINGS v3 — PDF Builder
Invocato da npm run build:pdf dopo che build/pdf-renderer.js ha
già generato dist/Mythic_Rings_v3.html
"""
import sys, os, time, logging, subprocess, shutil

# Sopprimi warning non critici di WeasyPrint e fontTools
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('fontTools').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

try:
    import weasyprint
except ImportError:
    print('  ✗  weasyprint non installato. Esegui: pip install weasyprint')
    sys.exit(1)

dist_dir  = sys.argv[1] if len(sys.argv) > 1 else './dist'
html_path = os.path.join(dist_dir, 'Mythic_Rings_v3.html')
pdf_path  = os.path.join(dist_dir, 'Mythic_Rings_v3.pdf')

if not os.path.exists(html_path):
    print(f'  ✗  HTML non trovato: {html_path}')
    print('     Esegui prima: node build/pdf-renderer.js')
    sys.exit(1)

print(f'\n📄 WeasyPrint → {pdf_path}\n')
t0 = time.time()

doc = weasyprint.HTML(filename=os.path.abspath(html_path))
doc.write_pdf(pdf_path)

elapsed = time.time() - t0
kb = os.path.getsize(pdf_path) // 1024
print(f'  ✅  Mythic_Rings_v3.pdf  ({kb} KB  in {elapsed:.1f}s)\n')
