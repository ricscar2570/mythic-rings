#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data/playtest/phase3_internal_plan.yml'
d=yaml.safe_load(p.read_text(encoding='utf-8'))
errors=[]
blocks=d.get('blocks',{})
sessions=d.get('sessions',[])
if set(blocks)!={'A','B','C','D','E','F'}:
    errors.append('blocchi attesi A-F')
if len(sessions)!=12:
    errors.append(f'attese 12 sessioni, trovate {len(sessions)}')
ids=[s.get('id') for s in sessions]
if len(set(ids))!=12:
    errors.append('ID sessione duplicati')
for b in 'ABCDEF':
    expected=blocks.get(b,{}).get('sessions',[])
    actual=[s.get('id') for s in sessions if s.get('block')==b]
    if len(actual)!=2 or actual!=expected:
        errors.append(f'blocco {b}: attese esattamente due sessioni coerenti, trovate {actual}')
covered={x for s in sessions for x in s.get('tests',[]) if isinstance(x,str) and x.startswith('B')}
missing={f'B{i}' for i in range(1,9)}-covered
if missing:
    errors.append(f'matrice B1-B8 incompleta: {sorted(missing)}')
thresholds=d.get('decision_thresholds',{})
expected_thresholds={
    'casata_decisive_share_warning':0.35,
    'unused_power_share_warning':0.30,
    'same_scene_cost_recovery_warning':0.50,
    'mictlan_healer_effect_warning':0.25,
    'minimum_comparable_observations_before_change':3,
}
for k,v in expected_thresholds.items():
    if thresholds.get(k)!=v:
        errors.append(f'soglia {k}: atteso {v}, trovato {thresholds.get(k)}')
if d.get('status')!='prepared_not_executed':
    errors.append('il piano Phase3 deve restare marcato prepared_not_executed finché non esistono sessioni reali')
if errors:
    print('Piano Fase 3 NON valido:')
    for e in errors: print('-',e)
    sys.exit(1)
print('Piano Fase 3 valido e non confuso con evidenza reale.')
print('  12 sessioni / 6 blocchi A-F')
print('  matrice B1-B8 coperta')
print('  soglie decisionali allineate al piano')
