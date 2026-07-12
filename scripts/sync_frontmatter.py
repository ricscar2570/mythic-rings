#!/usr/bin/env python3
from pathlib import Path
import re

VERSION = '0.9.0-beta.1'
for path in sorted(Path('chapters').glob('*.md')):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise SystemExit(f'frontmatter assente: {path}')
    end = text.find('\n---\n', 4)
    if end < 0:
        raise SystemExit(f'frontmatter non chiuso: {path}')
    front = text[4:end]
    body = text[end+5:]
    front = re.sub(r'^status:\s*.*$', 'status: beta', front, flags=re.M)
    front = re.sub(r'^version:\s*.*$', f'version: {VERSION}', front, flags=re.M)
    path.write_text('---\n' + front + '\n---\n' + body, encoding='utf-8')
print('Frontmatter sincronizzato.')
