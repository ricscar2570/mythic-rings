#!/usr/bin/env python3
from pathlib import Path
import csv, statistics, math, sys

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.')

def read(name):
    p=ROOT/name
    if not p.exists(): return []
    with p.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def num(x):
    try: return float(x)
    except: return None

def pct(n,d): return None if not d else 100*n/d

def pctl(vals,q):
    vals=sorted(v for v in vals if v is not None)
    if not vals:return None
    k=(len(vals)-1)*q; lo=math.floor(k); hi=math.ceil(k)
    return vals[lo] if lo==hi else vals[lo]*(hi-k)+vals[hi]*(k-lo)

def fmt(v,suffix=''):
    return 'n/a' if v is None else f'{v:.1f}{suffix}'

sessions=read('blind_sessions.csv')
cons=read('blind_consultations.csv')
ris=read('blind_risonanza.csv')
combats=read('blind_combats.csv')
cases=read('blind_rule_cases.csv')
issues=read('blind_issues.csv')

print('MYTHIC RINGS - BLIND REPORT')
print('Sessions:',len(sessions),'Groups:',len(set(r.get('group_id','') for r in sessions if r.get('group_id'))))
ct=[num(r.get('seconds')) for r in cons if num(r.get('seconds')) is not None]
print('Consultations:',len(cons),'median',fmt(statistics.median(ct) if ct else None,'s'),'p90',fmt(pctl(ct,.9),'s'))
found=[r for r in cons if r.get('found','').lower() in ('1','true','yes','si','sì')]
correct=[r for r in cons if r.get('applied_correctly','').lower() in ('1','true','yes','si','sì')]
print('Consult found:',fmt(pct(len(found),len(cons)),'%'),'Applied correctly:',fmt(pct(len(correct),len(cons)),'%'))
case_valid=[r for r in cases if r.get('correct','')!='']
case_ok=[r for r in case_valid if r.get('correct','').lower() in ('1','true','yes','si','sì')]
print('Standardized cases correct:',fmt(pct(len(case_ok),len(case_valid)),'%'),f'({len(case_ok)}/{len(case_valid)})')
rt=[num(r.get('seconds_to_offer')) for r in ris if num(r.get('seconds_to_offer')) is not None]
valid=[r for r in ris if r.get('two_valid_prices','').lower() in ('1','true','yes','si','sì')]
accepted=[r for r in ris if r.get('accepted','').lower() in ('1','true','yes','si','sì')]
refused=[r for r in ris if r.get('accepted','').lower() in ('0','false','no')]
print('Risonanza:',len(ris),'two valid',fmt(pct(len(valid),len(ris)),'%'),'median offer',fmt(statistics.median(rt) if rt else None,'s'),'accepted/refused',len(accepted),'/',len(refused))
cr=[num(r.get('rounds')) for r in combats if num(r.get('rounds')) is not None]
print('Combats:',len(combats),'median rounds',fmt(statistics.median(cr) if cr else None))
sev={k:sum(1 for r in issues if r.get('severity','').upper()==k) for k in ('P0','P1','P2')}
print('Issues:',sev)
print('\nGATE FLAGS')
case_rate=pct(len(case_ok),len(case_valid)); med=statistics.median(ct) if ct else None; p90=pctl(ct,.9)
print('Procedures >=95%:', 'PASS' if case_rate is not None and case_rate>=95 else 'PENDING/FAIL')
print('Consult median <30s:', 'PASS' if med is not None and med<30 else 'PENDING/FAIL')
print('Consult p90 <90s:', 'PASS' if p90 is not None and p90<90 else 'PENDING/FAIL')
print('No P0:', 'PASS' if sev['P0']==0 else 'FAIL')
