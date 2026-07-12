#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'adversaries.yml'
OUT = ROOT / 'chapters' / '26_il_bestiario_di_milano.md'

def load():
    return yaml.safe_load(DATA.read_text(encoding='utf-8'))

def render_entry(a):
    tags = ', '.join(a['tags'])
    moves = '\n'.join(f'- **{m["name"]}:** {m["text"]}' for m in a['moves'])
    return f''':::box[{a['name']}]{{type=info}}
*{a['description']}*

| PF | Armatura | Danno | LS | Tipo |
|---:|---:|---|---:|---|
| {a['pf']} | {a['armor']} | {a['damage']} | {a['ls']} | {a['type']} |

**Impulso:** {a['impulse']}  
**Tag:** {tags}

**Mosse**
{moves}

**Debolezza:** {a['weakness']}  
**Comportamento:** {a['behavior']}  
**Hook:** *{a['hook']}*
:::
'''

def main():
    data=load()
    entries=data['adversaries']
    by_band={}
    for a in entries:
        band = '1–2' if a['ls'] <= 2 else '3–4' if a['ls'] <= 4 else '5–6' if a['ls'] <= 6 else '7–8' if a['ls'] <= 8 else '9–10'
        by_band.setdefault(band,[]).append(a['name'])
    index_rows=[]
    labels={'1–2':'Minion','3–4':'Comuni','5–6':'Forti','7–8':'Elite','9–10':'Leggendari'}
    for band in ['1–2','3–4','5–6','7–8','9–10']:
        index_rows.append(f"| {band} | {labels[band]} | {', '.join(by_band.get(band,[]))} |")
    body='''---
title: "Il Bestiario di Milano"
chapter: 26
part: "Parte VI: Bestiario e Avventure"
section: "Bestiario e Avventure"
epigraph: "Milano ha i suoi mostri. Alcuni li conosci già."
tags: [bestiario, avversari]
status: beta
version: 0.9.0-beta.1
---

## Il Bestiario di Milano

Gli avversari di *Mythic Rings* non effettuano tiri. Ogni stat block indica PF, Armatura, danno, Livello di Sfida, impulso, tag e Mosse. Il Custode rende concrete le Mosse come conseguenza dei tiri, quando una minaccia annunciata viene ignorata e alla fine del round se la creatura è libera di agire.

Il danno riportato è quello inflitto quando la creatura ottiene un'apertura reale. Le qualità descritte nella fiction possono rendere impossibile un'azione, richiedere una preparazione o imporre una Mossa prima ancora del danno.

| LS | Categoria | Creature |
|---:|---|---|
'''+ '\n'.join(index_rows) + '''

### Leggere uno stat block

- **Impulso:** ciò che la creatura cerca di fare quando nessuno la ostacola.
- **Tag:** qualità che modificano possibilità e posizione narrativa.
- **Mosse:** azioni concrete che il Custode può annunciare e rendere effettive.
- **Debolezza:** modo specifico di ridurre il vantaggio della creatura; non sempre significa danno maggiore.
- **Comportamento:** criteri per reazione, fuga e negoziazione.

'''
    body += '\n'.join(render_entry(a) for a in entries)
    body += '''\n:::box[Creare varianti]{type=tip}
Per creare una variante, modifica una sola dimensione alla volta: impulso, ambiente, una Mossa o una debolezza. Se aumenti PF, danno e numero di azioni insieme, rivaluta anche il Livello di Sfida attraverso il playtest.
:::
'''
    OUT.write_text(body, encoding='utf-8')
    print(f'Generato {OUT} con {len(entries)} avversari.')

if __name__=='__main__': main()
