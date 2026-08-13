#!/usr/bin/env python3
"""Aggregate real Mythic Rings playtest bundles without inventing evidence."""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path


def median(xs):
    return statistics.median(xs) if xs else None

def pct(n,d):
    return (100*n/d) if d else None

def fmt_pct(x):
    return 'n/a' if x is None else f'{x:.1f}%'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--out', default='docs/playtest/reports')
    args=ap.parse_args()
    bundles=[]
    for raw in args.files:
        p=Path(raw)
        try: bundles.append(json.loads(p.read_text(encoding='utf-8')))
        except Exception as e:
            print(f'ERRORE {p}: {e}',file=sys.stderr); return 1
    if not bundles:
        print('Nessun bundle.',file=sys.stderr); return 1

    sessions=[b['session'] for b in bundles]
    chars=[c for b in bundles for c in b.get('characters',[])]
    res=[r for b in bundles for r in b.get('resonance_events',[])]
    combat=[r for b in bundles for r in b.get('combat_rounds',[])]
    lookups=[r for b in bundles for r in b.get('rule_lookups',[])]
    issues=[r for b in bundles for r in b.get('issues',[])]

    accepted=[r for r in res if r.get('procedure_started') and r.get('choice')!='rifiuto']
    refused=[r for r in res if r.get('procedure_started') and r.get('choice')=='rifiuto']
    fully_valid=[r for r in res if r.get('procedure_started') and r.get('price_1_valid') and r.get('price_2_valid')]
    choice_counts=Counter(r.get('choice') for r in accepted)
    all_offered=Counter()
    for r in res:
        if r.get('procedure_started'):
            all_offered[r.get('price_1_category')]+=1; all_offered[r.get('price_2_category')]+=1

    decisive=Counter(); powers=Counter(); resource_delta=defaultdict(list)
    for c in chars:
        cas=c.get('casata'); decisive[cas]+=c.get('decisive_resolutions',0); powers[cas]+=c.get('powers_used',0)
        resource_delta[cas].append({
            'pf':c.get('end_pf',0)-c.get('start_pf',0),
            'stress':c.get('end_stress',0)-c.get('start_stress',0),
            'corruption':c.get('end_corruption',0)-c.get('start_corruption',0),
        })
    total_dec=sum(decisive.values())

    second_yes=sum(b.get('post_session',{}).get('second_session_yes_count',0) for b in bundles)
    second_no=sum(b.get('post_session',{}).get('second_session_no_count',0) for b in bundles)

    data={
        'session_count':len(bundles),
        'group_count':len(set(s.get('group_id') for s in sessions)),
        'rules_versions':sorted(set(s.get('rules_version') for s in sessions)),
        'resonance':{
            'events':len(res),'started':sum(bool(r.get('procedure_started')) for r in res),
            'accepted':len(accepted),'refused':len(refused),
            'acceptance_rate_pct':pct(len(accepted),len(accepted)+len(refused)),
            'refusal_rate_pct':pct(len(refused),len(accepted)+len(refused)),
            'fully_valid_offer_rate_pct':pct(len(fully_valid),sum(bool(r.get('procedure_started')) for r in res)),
            'median_decision_seconds':median([r.get('decision_seconds',0) for r in res if r.get('procedure_started')]),
            'median_clarity':median([r.get('clarity_rating') for r in res if r.get('clarity_rating') is not None]),
            'median_relevance':median([r.get('relevance_rating') for r in res if r.get('relevance_rating') is not None]),
            'median_difficulty':median([r.get('difficulty_rating') for r in res if r.get('difficulty_rating') is not None]),
            'consequence_return_rate_pct':pct(sum(bool(r.get('consequence_returned_in_fiction')) for r in accepted),len(accepted)),
            'choices':dict(choice_counts),'offers_by_category':dict(all_offered),
        },
        'rules_lookup':{
            'count':len(lookups),'median_seconds':median([x.get('elapsed_seconds',0) for x in lookups]),
            'correct_application_rate_pct':pct(sum(bool(x.get('applied_correctly')) for x in lookups),len(lookups)),
        },
        'combat':{
            'rounds':len(combat),'duplicate_enemy_action_flags':sum(bool(x.get('possible_duplicate_enemy_action')) for x in combat),
            'order_doubts':sum(x.get('order_doubts',0) for x in combat),
            'rule_lookups':sum(x.get('rule_lookups',0) for x in combat),
            'damage_to_guardians':sum(x.get('damage_to_guardians',0) for x in combat),
            'damage_to_adversaries':sum(x.get('damage_to_adversaries',0) for x in combat),
        },
        'spotlight':{'decisive_resolutions':dict(decisive),'shares_pct':{k:pct(v,total_dec) for k,v in decisive.items()}},
        'powers_used':dict(powers),
        'second_session':{'yes':second_yes,'no':second_no,'yes_rate_pct':pct(second_yes,second_yes+second_no)},
        'issues':{'count':len(issues),'by_severity':dict(Counter(x.get('severity') for x in issues)),'by_category':dict(Counter(x.get('category') for x in issues))},
    }

    red=[]; rr=data['resonance']
    if rr['started']>=30 and rr['acceptance_rate_pct'] is not None and rr['acceptance_rate_pct']>75: red.append('Risonanza: accettazione >75% dopo almeno 30 offerte.')
    if rr['started']>=30 and rr['refusal_rate_pct'] is not None and rr['refusal_rate_pct']<15: red.append('Risonanza: rifiuto <15% dopo almeno 30 offerte.')
    if rr['median_decision_seconds'] is not None and rr['median_decision_seconds']>45: red.append('Risonanza: mediana decisione >45 secondi.')
    if rr['started'] and rr['fully_valid_offer_rate_pct'] is not None and rr['fully_valid_offer_rate_pct']<90: red.append('Risonanza: più del 10% delle offerte avviate contiene almeno un prezzo segnato non valido.')
    if data['combat']['duplicate_enemy_action_flags']>0: red.append('Combattimento: rilevata almeno una possibile doppia Azione Significativa nemica.')
    if data['rules_lookup']['median_seconds'] is not None and data['rules_lookup']['median_seconds']>=60: red.append('Consultazione: mediana >=60 secondi.')
    for cas,share in data['spotlight']['shares_pct'].items():
        if share is not None and share>35: red.append(f'Spotlight: {cas} supera il 35% delle risoluzioni decisive nel campione aggregato; verificare tre sessioni consecutive prima di intervenire.')
    data['red_flags']=red

    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    (out/'playtest_aggregate.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=[
        '# Mythic Rings — Report aggregato playtest','',
        f'**Sessioni:** {data["session_count"]}  ',f'**Gruppi:** {data["group_count"]}  ',f'**Versioni:** {", ".join(data["rules_versions"])}','',
        '## Risonanza','',
        f'- Eventi: {rr["events"]}; procedure avviate: {rr["started"]}.',
        f'- Accettazione: {fmt_pct(rr["acceptance_rate_pct"])}; rifiuto: {fmt_pct(rr["refusal_rate_pct"])}.',
        f'- Offerte con entrambi i prezzi segnati validi: {fmt_pct(rr["fully_valid_offer_rate_pct"])}.',
        f'- Mediana decisione: {rr["median_decision_seconds"] if rr["median_decision_seconds"] is not None else "n/a"} s.',
        f'- Mediane chiarezza / pertinenza / difficoltà: {rr["median_clarity"]} / {rr["median_relevance"]} / {rr["median_difficulty"]}.',
        f'- Conseguenza ritornata in fiction: {fmt_pct(rr["consequence_return_rate_pct"])} delle Risonanze accettate.','',
        '## Consultazione e combattimento','',
        f'- Consultazioni: {data["rules_lookup"]["count"]}; mediana {data["rules_lookup"]["median_seconds"]} s; applicazione corretta {fmt_pct(data["rules_lookup"]["correct_application_rate_pct"])}.',
        f'- Round registrati: {data["combat"]["rounds"]}; flag doppia azione nemica: {data["combat"]["duplicate_enemy_action_flags"]}; dubbi ordine: {data["combat"]["order_doubts"]}.','',
        '## Spotlight','']
    for cas,v in sorted(data['spotlight']['decisive_resolutions'].items()): md.append(f'- {cas}: {v} risoluzioni decisive ({fmt_pct(data["spotlight"]["shares_pct"].get(cas))}).')
    md += ['', '## Desiderio di seconda sessione','',f'- Sì: {second_yes}; No: {second_no}; tasso sì: {fmt_pct(data["second_session"]["yes_rate_pct"])}.','', '## Red flag automatiche','']
    md += [f'- {x}' for x in red] if red else ['- Nessuna red flag automatica attivata con i dati disponibili.']
    md += ['', '> Questo report segnala pattern; non sostituisce il triage qualitativo né autorizza modifiche su un singolo outlier.','']
    (out/'playtest_aggregate.md').write_text('\n'.join(md),encoding='utf-8')
    print(f'Analizzate {len(bundles)} sessioni. Report: {out}')
    return 0
if __name__=='__main__': raise SystemExit(main())
