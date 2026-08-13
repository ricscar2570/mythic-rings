#!/usr/bin/env python3
"""Gate-oriented validation for Mythic Rings Phase 2 rules consolidation.

This validator proves source consistency and regression protection only. It does
NOT substitute the independent-GM / human-playtest acceptance criteria required
by the development plan for G2.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        fail(f"File assente: {rel}")
        return ""
    return p.read_text(encoding="utf-8")


def load_yaml(rel: str):
    text = read(rel)
    if not text:
        return None
    try:
        return yaml.safe_load(text)
    except Exception as exc:  # pragma: no cover - surfaced to CLI
        fail(f"YAML non valido {rel}: {exc}")
        return None


rules_doc = load_yaml("data/canonical_rules.yml") or {}
rules = rules_doc.get("rules", {}) if isinstance(rules_doc, dict) else {}
expected_ids = {f"MR-RULE-{n:03d}" for n in range(1, 19)}
actual_ids = {v.get("id") for v in rules.values() if isinstance(v, dict)}
if actual_ids != expected_ids:
    fail(f"ID regole canoniche: attesi MR-RULE-001..018, trovati {sorted(x for x in actual_ids if x)}")
if rules_doc.get("product_version") != "0.9.0-beta.2":
    fail("data/canonical_rules.yml non è sincronizzato a 0.9.0-beta.2")

# R2.1 — Risonanza: 4 Casate x 4 categorie x 6 esempi = 96.
prices = load_yaml("data/risonanza_price_examples.yml") or {}
casate = prices.get("casate", {}) if isinstance(prices, dict) else {}
expected_casate = {"Avalon", "Umbra", "Ife", "Mictlan"}
expected_categories = {"Corpo", "Anima", "Legame", "Mondo"}
if set(casate) != expected_casate:
    fail(f"Libreria Risonanza: Casate non canoniche: {sorted(casate)}")
count = 0
for casata in sorted(expected_casate):
    categories = casate.get(casata, {})
    if set(categories) != expected_categories:
        fail(f"Libreria Risonanza {casata}: categorie attese {sorted(expected_categories)}, trovate {sorted(categories)}")
    for category in sorted(expected_categories):
        examples = categories.get(category, [])
        if len(examples) != 6:
            fail(f"Libreria Risonanza {casata}/{category}: attesi 6 esempi, trovati {len(examples)}")
        count += len(examples)
if count != 96:
    fail(f"Libreria Risonanza: attesi 96 esempi, trovati {count}")

ring = rules.get("ring_resonance", {})
if "consequence_replacement" not in ring or "Non si applica anche la conseguenza" not in str(ring.get("consequence_replacement", "")):
    fail("MR-RULE-015 non esplicita la sostituzione della conseguenza originaria")
if "Usare Potere" not in str(ring.get("eligibility", "")) or "Mosse Esclusive" not in str(ring.get("eligibility", "")):
    fail("MR-RULE-015 non limita chiaramente l'eleggibilità")
price_lib = read("docs/rules/RISONANZA_PRICE_LIBRARY.md")
for marker in ["45 secondi", "Vago:", "Retroattivo:", "Sproporzionato:", "Anima senza uscita"]:
    if marker.lower() not in price_lib.lower():
        fail(f"Libreria Risonanza: manca copertura operativa per '{marker}'")

# R2.2 — four ring states, no old automatic-renunciation formulation.
states = rules.get("ring_bond_states", {}).get("states", {})
if set(states) != {"removed", "temporary_separation", "cession", "renunciation"}:
    fail(f"MR-RULE-017: quattro stati non completi, trovati {sorted(states)}")
for rel in [
    "chapters/02_i_custodi_e_gli_anelli_di_custodia.md",
    "chapters/04_creare_il_tuo_guardiano.md",
    "chapters/32_domande_frequenti_faq.md",
    "products/quickstart/Mythic_Rings_Quickstart.md",
    "products/player-kit/Mythic_Rings_Kit_del_Giocatore.md",
]:
    txt = read(rel).lower()
    if "rinuncia" not in txt:
        fail(f"{rel}: manca allineamento esplicito alla Rinuncia")
old_ring_phrases = [
    "togliere l'anello equivale alla rinuncia",
    "rimuovere l'anello equivale alla rinuncia",
    "togliere l'anello è rinuncia",
    "se togli l'anello rinunci automaticamente",
]
user_corpus = "\n".join(read(str(p.relative_to(ROOT))) for base in [ROOT / "chapters", ROOT / "products"] for p in base.rglob("*.md"))
for phrase in old_ring_phrases:
    if phrase in user_corpus.lower():
        fail(f"Regressione MR-RULE-017: formulazione obsoleta rilevata: {phrase}")

# R2.3 — threat action budget and worked example.
combat = rules.get("combat_flow", {})
for key in ["threat_unit", "significant_action", "enemies", "reset"]:
    if not combat.get(key):
        fail(f"MR-RULE-008 incompleta: manca {key}")
for rel in [
    "chapters/05_come_si_gioca.md",
    "chapters/20_bilanciare_il_combattimento.md",
    "chapters/31_quick_reference_custode.md",
    "products/quickstart/Mythic_Rings_Quickstart.md",
]:
    txt = read(rel)
    if "Azione Significativa" not in txt:
        fail(f"{rel}: non esplicita il budget di Azione Significativa")
combat_example = read("docs/rules/COMBAT_ROUND_EXAMPLE.md")
for name in ["Marco", "Chiara", "Luca", "Elena"]:
    if name not in combat_example:
        fail(f"Esempio round: manca il Guardiano {name}")
for marker in ["Segugi", "gruppo di minion", "Dullahan", "budget"]:
    if marker.lower() not in combat_example.lower():
        fail(f"Esempio round incompleto: manca '{marker}'")

# R2.4 — Escalation once per Main Action; five edge cases.
escalation = rules.get("escalation", {})
application = str(escalation.get("application", ""))
if "una volta per Azione Principale" not in application:
    fail("MR-RULE-009: manca il limite una volta per Azione Principale")
for marker in ["bersagli", "colpi"]:
    if marker not in application:
        fail(f"MR-RULE-009: manca il caso '{marker}'")
esc_cases = read("docs/rules/ESCALATION_CASES.md")
headings = re.findall(r"^##\s+Caso\s+\d+", esc_cases, flags=re.M | re.I)
if len(headings) != 5:
    fail(f"Escalation: attesi 5 casi limite principali, trovati {len(headings)}")

# R2.5 — terminology, Burnout, anti-cycle source.
stress = rules.get("stress_corruption", {})
terminology = stress.get("terminology", {})
for key in ["suffer_stress", "recover_stress", "spend_hp", "suffer_damage", "lose_hp"]:
    if not terminology.get(key):
        fail(f"MR-RULE-012: manca verbo canonico {key}")
burnout_text = str(stress.get("stress", {}))
for marker in ["sovraccarico", "2 PF", "Sfidare il Pericolo", "1d6"]:
    if marker not in burnout_text:
        fail(f"MR-RULE-012 Burnout: manca '{marker}'")

source_paths = [p for base in [ROOT / "chapters", ROOT / "products", ROOT / "data"] for p in base.rglob("*.md")]
source_paths += [p for p in (ROOT / "data").rglob("*.yml")]
for p in source_paths:
    txt = p.read_text(encoding="utf-8")
    rel = p.relative_to(ROOT)
    forbidden = [
        r"\briduci(?:\s+lo)?\s+Stress\b",
        r"\bridurre(?:\s+lo)?\s+Stress\b",
        r"\briduce\s+Stress\b",
        r"\bperd(?:i|ere)\s+\d+(?:d\d+)?\s+Stress\b",
        r"\bprendi\s+\d+(?:d\d+)?\s+Stress\b",
        r"\bcostano il doppio\b",
        r"\bcosto raddoppia\b",
    ]
    for pat in forbidden:
        if re.search(pat, txt, flags=re.I):
            fail(f"Terminologia/vecchio Burnout in {rel}: pattern {pat}")

ch5 = read("chapters/05_come_si_gioca.md")
if ch5.count("## Nessun ciclo a guadagno netto") != 1:
    fail("La regola generale anti-ciclo non ha un unico heading normativo nel Capitolo 5")
for rel in ["chapters/03_le_quattro_casate.md", "chapters/09_poteri_di_ife.md", "chapters/10_poteri_di_mictlan.md"]:
    txt = read(rel)
    if "Nessun ciclo a guadagno netto" not in txt or "Capitolo 5" not in txt:
        fail(f"{rel}: l'eccezione/limite locale non rinvia alla regola anti-ciclo proprietaria")

# R2.6 — Sangue Tenace calculations.
blood = rules.get("mictlan_blood", rules.get("mictlan_blood_tenacity", rules.get("blood_tenacity", {})))
if not blood:
    # Locate by rule id in case the storage key changes.
    blood = next((v for v in rules.values() if isinstance(v, dict) and v.get("id") == "MR-RULE-013"), {})
for marker in ["40%", "floor", "2 Stress"]:
    if marker not in str(blood):
        fail(f"MR-RULE-013 Sangue Tenace: manca '{marker}'")

def sangue(cost: int) -> tuple[int, int] | None:
    if cost < 2:
        return None
    converted = min(max(math.floor(cost / 2), 1), cost - 1)
    return cost - converted, converted
expected = {1: None, 2: (1, 1), 3: (2, 1), 5: (3, 2)}
actual = {c: sangue(c) for c in expected}
if actual != expected:
    fail(f"Sangue Tenace: regressione formula {actual} != {expected}")
blood_manual = read("chapters/10_poteri_di_mictlan.md")
for marker in ["| 1 PF |", "| 2 PF |", "| 3 PF |", "| 5 PF |", "40%"]:
    if marker.lower() not in blood_manual.lower():
        fail(f"Capitolo Mictlan: manca esempio Sangue Tenace '{marker}'")

# P0-05 — one global Veil scale; allow only explicit negations of old Exposure scale.
veil = rules.get("veil_tracker", {})
if veil.get("range") != "0-12" and veil.get("range") != "0–12":
    # YAML may parse a plain unquoted 0-12 as string, retain explicit check.
    fail(f"MR-RULE-018: range inatteso {veil.get('range')!r}")
campaign = read("chapters/27_campagna_il_crepuscolo_del_velo.md")
for old in ["Esposizione pubblica 0–4", "Esposizione pubblica 0-4", "Tracker Esposizione", "Esposizione Tracker"]:
    if old.lower() in campaign.lower():
        fail(f"Campagna: scala meccanica obsoleta rilevata: {old}")
if "Velo Tracker canonico 0–12" not in campaign:
    fail("Campagna: manca riferimento esplicito al Velo Tracker 0–12")

# Product/pregen regression: standalone onboarding materials must use current four pregens.
for rel in ["products/quickstart/Mythic_Rings_Quickstart.md", "products/adventure/Mythic_Rings_Notte_al_Monumentale.md"]:
    txt = read(rel)
    # Specific old-pregen usage, not lore references elsewhere.
    if "interessa Leila o Marco" in txt or "per Kwame che" in txt:
        fail(f"{rel}: vecchi nomi da pregenerato ancora presenti")

# Glossary and style contract.
glossary = read("chapters/29_glossario_dei_termini.md")
for term in ["Azione Significativa", "Rinuncia", "Sangue Tenace", "Velo Tracker"]:
    if f"| {term} |" not in glossary:
        fail(f"Glossario: manca {term}")
style = read("docs/EDITORIAL_STYLE_GUIDE.md")
for marker in ["subire Stress", "recuperare Stress", "Azione Significativa", "Custode"]:
    if marker not in style:
        fail(f"Style guide: manca contratto '{marker}'")

# Canon NPCs should not be used as player examples in core procedure chapters.
for rel in ["chapters/05_come_si_gioca.md", "chapters/17_le_mosse_del_custode.md"]:
    txt = read(rel)
    for old_player in ["Leila ottiene", "Leila osserva un emissario"]:
        if old_player in txt:
            fail(f"{rel}: PNG canonico riusato come esempio di giocatore: '{old_player}'")

if errors:
    print("Gate G2 — validazione sorgenti Fase 2: FAIL")
    for err in errors:
        print(f"ERRORE: {err}")
    sys.exit(1)

print("Gate G2 — validazione sorgenti Fase 2: PASS tecnico")
print(f"  Regole canoniche: {len(actual_ids)} (MR-RULE-001..018)")
print(f"  Prezzi Risonanza: {count} (4 Casate x 4 categorie x 6)")
print("  Stati Anello: 4 + morte separata")
print("  Budget minacce: fonte canonica + esempio completo presenti")
print("  Escalation: 5 casi limite presenti")
print("  Terminologia Stress/PF e Burnout: regressioni note assenti")
print("  Sangue Tenace: esempi 1/2/3/5 e formula coerenti")
print("  Velo: unica scala globale 0–12")
print("NOTA: G2 resta PENDING finché i criteri umani del piano non hanno evidenza indipendente.")
