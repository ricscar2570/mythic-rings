#!/usr/bin/env bash
set -euo pipefail

TARGET=${1:?target checkout required}
SOURCE_ARCHIVE=${2:?source archive required}
EXPECTED_HEAD=f0c83d33761a9c47cb1146ac6f49db9261a676c5

cd "$TARGET"
ACTUAL_HEAD=$(git rev-parse HEAD)
if [[ "$ACTUAL_HEAD" != "$EXPECTED_HEAD" ]]; then
  echo "Target branch moved: expected $EXPECTED_HEAD, found $ACTUAL_HEAD" >&2
  exit 20
fi

PRESERVE=$(mktemp -d)
trap 'rm -rf "$PRESERVE"' EXIT

[[ -d sources ]] && cp -a sources "$PRESERVE/sources"
[[ -d "vecchio sito" ]] && cp -a "vecchio sito" "$PRESERVE/vecchio sito"
[[ -f build/product-reference.docx ]] && {
  mkdir -p "$PRESERVE/build"
  cp build/product-reference.docx "$PRESERVE/build/product-reference.docx"
}
[[ -f archive/baselines/0.9.0-beta.2/source_snapshot.tar.gz ]] && {
  mkdir -p "$PRESERVE/archive/baselines/0.9.0-beta.2"
  cp archive/baselines/0.9.0-beta.2/source_snapshot.tar.gz "$PRESERVE/archive/baselines/0.9.0-beta.2/source_snapshot.tar.gz"
}

find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
tar -xJf "$SOURCE_ARCHIVE" -C .

[[ -d "$PRESERVE/sources" ]] && cp -a "$PRESERVE/sources" ./sources
[[ -d "$PRESERVE/vecchio sito" ]] && cp -a "$PRESERVE/vecchio sito" "./vecchio sito"
[[ -f "$PRESERVE/build/product-reference.docx" ]] && {
  mkdir -p build
  cp "$PRESERVE/build/product-reference.docx" build/product-reference.docx
}
[[ -f "$PRESERVE/archive/baselines/0.9.0-beta.2/source_snapshot.tar.gz" ]] && {
  mkdir -p archive/baselines/0.9.0-beta.2
  cp "$PRESERVE/archive/baselines/0.9.0-beta.2/source_snapshot.tar.gz" archive/baselines/0.9.0-beta.2/source_snapshot.tar.gz
}

rm -rf dist node_modules assets/fonts build/__pycache__ scripts/__pycache__ tests/__pycache__
find . -type d -name __pycache__ -prune -exec rm -rf {} +
find . -type f -name '*.pyc' -delete

python3 scripts/check_repository_portability.py
python3 - <<'PY'
from pathlib import Path
import yaml
root = Path('.')
book = yaml.safe_load((root / 'book.yml').read_text(encoding='utf-8'))
assert str(book['version']) == '0.9.0-beta.4.2', book['version']
assert not (root / 'dist').exists()
assert not (root / 'assets/fonts').exists()
print('Source import verified:', book['version'])
PY
