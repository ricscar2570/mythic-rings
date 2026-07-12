'use strict';
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

function findRoot(start = __dirname) {
  let dir = path.resolve(start);
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, 'book.yml'))) return dir;
    dir = path.dirname(dir);
  }
  throw new Error('book.yml non trovato');
}

function loadMeta(start) {
  const root = findRoot(start || __dirname);
  const meta = yaml.load(fs.readFileSync(path.join(root, 'book.yml'), 'utf8'));
  if (!meta || !meta.title || !meta.version || !meta.output_basename) {
    throw new Error('book.yml incompleto: title, version e output_basename sono obbligatori');
  }
  return { ...meta, root };
}

module.exports = { loadMeta, findRoot };
