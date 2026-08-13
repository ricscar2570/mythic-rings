#!/usr/bin/env python3
"""Audit semantico minimo dei contenuti canonici di Mythic Rings."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


meta = yaml.safe_load((ROOT / "book.yml").read_text(encoding="utf-8"))

# Manifesto e frontmatter.
seen_numbers: set[int] = set()
seen_titles: set[str] = set()
for rel in meta["chapters"]:
    path = ROOT / rel
    if not path.exists():
        fail(f"Capitolo dichiarato ma assente: {rel}")
        continue
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", raw, re.S)
    if not match:
        fail(f"Frontmatter assente: {rel}")
        continue
    fm = yaml.safe_load(match.group(1))
    number = fm.get("chapter")
    title = fm.get("title")
    if number in seen_numbers:
        fail(f"Numero capitolo duplicato: {number}")
    seen_numbers.add(number)
    if title in seen_titles:
        fail(f"Titolo capitolo duplicato: {title}")
    seen_titles.add(title)
    if fm.get("version") != meta["version"]:
        fail(f"Versione non allineata in {rel}")
    if fm.get("status") != meta["release_stage"]:
        fail(f"Stato non allineato in {rel}")

expected_numbers = set(range(1, len(meta["chapters"]) + 1))
if seen_numbers != expected_numbers:
    fail(f"Sequenza capitoli non continua: {sorted(seen_numbers)}")

# Catalogo poteri: 15 per Casata, 3 per livello.
power_files = {
    "avalon": ROOT / "chapters/07_poteri_di_avalon.md",
    "umbra": ROOT / "chapters/08_poteri_di_umbra.md",
    "ife": ROOT / "chapters/09_poteri_di_ife.md",
    "mictlan": ROOT / "chapters/10_poteri_di_mictlan.md",
}
all_power_names: set[str] = set()
for house, path in power_files.items():
    text = path.read_text(encoding="utf-8")
    names = re.findall(rf":::box\[([^\]]+)\]\{{type=casata_{house}\}}", text)
    duplicates = {n for n in names if names.count(n) > 1}
    if duplicates:
        fail(f"{house}: poteri duplicati: {sorted(duplicates)}")
    all_power_names.update(names)
    sections = re.split(r"^### Livello \d", text, flags=re.M)[1:]
    if len(sections) != 5:
        fail(f"{house}: attese 5 fasce di livello, trovate {len(sections)}")
    else:
        level_total = 0
        for idx, section in enumerate(sections, 1):
            count = len(re.findall(rf":::box\[[^\]]+\]\{{type=casata_{house}\}}", section))
            level_total += count
            if count != 3:
                fail(f"{house} livello {idx}: attesi 3 poteri, trovati {count}")
        if level_total != 15:
            fail(f"{house}: attesi 15 poteri di livello, trovati {level_total}")

# I poteri dei pregenerati devono esistere.
creation = (ROOT / "chapters/04_creare_il_tuo_guardiano.md").read_text(encoding="utf-8")
def normalize_name(value: str) -> str:
    return value.replace("’", "'").strip().casefold()

normalized_powers = {normalize_name(name) for name in all_power_names}
normalized_creation = normalize_name(creation)
for name in [
    "Luce Guida", "Scudo Radiante", "Guarigione Minore",
    "Fondersi nelle Ombre", "Occhi Notturni", "Lama d'Ombra",
    "Crescita Rapida", "Tocco Vitale", "Sensi Animali",
    "Vedere Oltre il Velo", "Tocco del Gelo", "Parlare con i Morti",
]:
    if normalize_name(name) not in normalized_powers:
        fail(f"Potere del pregenerato inesistente: {name}")
    if normalize_name(name) not in normalized_creation:
        fail(f"Potere del pregenerato non presente nel capitolo 4: {name}")

# Bestiario strutturato.
adversaries = yaml.safe_load((ROOT / "data/adversaries.yml").read_text(encoding="utf-8"))
if isinstance(adversaries, dict):
    adversaries = adversaries.get("adversaries", [])
if len(adversaries) != 31:
    fail(f"Attesi 31 avversari, trovati {len(adversaries)}")
required = {"name", "description", "pf", "armor", "damage", "ls", "type", "impulse", "tags", "moves", "weakness", "behavior", "hook"}
names: set[str] = set()
for item in adversaries:
    missing = required - set(item)
    if missing:
        fail(f"Avversario {item.get('name','?')}: campi mancanti {sorted(missing)}")
    name = item.get("name", "?")
    if name in names:
        fail(f"Avversario duplicato: {name}")
    names.add(name)
    if "attack" in item or "attacco" in item:
        fail(f"Avversario {name}: statistica Attacco vietata")
    armor = item.get("armor")
    if not isinstance(armor, int) or not 0 <= armor <= 4:
        fail(f"Avversario {name}: Armatura non valida ({armor})")
    ls = item.get("ls")
    if not isinstance(ls, int) or not 1 <= ls <= 10:
        fail(f"Avversario {name}: LS non valido ({ls})")
    if not isinstance(item.get("moves"), list) or len(item["moves"]) < 2:
        fail(f"Avversario {name}: servono almeno due Mosse")
    if not re.search(r"\d+d\d+|\d+", str(item.get("damage", "")), re.I):
        fail(f"Avversario {name}: danno non interpretabile ({item.get('damage')})")

# Prodotti derivati: niente placeholder o versione storica.
for path in [
    ROOT / "products/quickstart/Mythic_Rings_Quickstart.md",
    ROOT / "products/player-kit/Mythic_Rings_Kit_del_Giocatore.md",
    ROOT / "products/adventure/Mythic_Rings_Notte_al_Monumentale.md",
]:
    text = path.read_text(encoding="utf-8")
    fm_match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not fm_match:
        fail(f"{path.relative_to(ROOT)}: frontmatter assente")
    else:
        product_fm = yaml.safe_load(fm_match.group(1))
        if str(product_fm.get("version")) != str(meta["version"]):
            fail(f"{path.relative_to(ROOT)}: versione {product_fm.get('version')} diversa da {meta['version']}")
    for pattern, label in [
        (r"\[[A-ZÀ-Ü][^\]]*(?:nome|cognome|email|sito|playtester)[^\]]*\]", "placeholder"),
        (r"Mythic Rings v3", "versione storica"),
        (r"ISBN\s*:?\s*000", "ISBN fittizio"),
    ]:
        if re.search(pattern, text, re.I):
            fail(f"{path.relative_to(ROOT)}: {label}")

# Frasi meccaniche obsolete ad alto rischio.
corpus = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in meta["chapters"])
for pattern, label in [
    (r"ritira(?:re)?\s+(?:entrambi|tutti e due)\s+i\s+dadi", "Fato: ritiro di entrambi i dadi"),
    (r"Dado Escalation[^\n]{0,120}(?:tiro|tiri|2d6)", "Escalation applicata ai tiri"),
    (r"Armatura\s+(?:totale\s+)?(?:massima|max)\s*[:=]?\s*[5-9]", "Armatura ordinaria oltre il limite"),
    (r"Punto Fato extra", "Fato oltre il massimo canonico"),
    (r"\+1 forward al primo tiro di ogni scontro", "bonus ad hoc per gruppi piccoli"),
]:
    hits = re.findall(pattern, corpus, re.I)
    if hits:
        fail(f"Regola obsoleta rilevata ({label}): {len(hits)} occorrenze")

# Ring Core: parità semantica e collisioni ad alto rischio.
canonical = yaml.safe_load((ROOT / "data/canonical_rules.yml").read_text(encoding="utf-8"))
ring = canonical.get("rules", {}).get("ring_resonance", {})
anchor = canonical.get("rules", {}).get("ring_anchor", {})
if ring.get("id") != "MR-RULE-015":
    fail("Risonanza: MR-RULE-015 assente")
if anchor.get("id") != "MR-RULE-016":
    fail("Ancora: MR-RULE-016 assente")
if not re.search(r"una volta per scena", str(ring.get("frequency", "")), re.I):
    fail("Risonanza: frequenza diversa da 1/scena")
if not re.search(r"non si resetta", str(ring.get("scene_boundary", "")), re.I) or not re.search(r"nuovo round", str(ring.get("scene_boundary", "")), re.I):
    fail("Risonanza: confine di scena non definito contro reset tattici")
if set((ring.get("prices") or {}).keys()) != {"body", "soul", "bond", "world"}:
    fail("Risonanza: categorie di prezzo non canoniche")
if not re.search(r"Usare Potere", str(ring.get("trigger", "")), re.I) or not re.search(r"Mossa Esclusiva di Casata", str(ring.get("trigger", "")), re.I):
    fail("Risonanza: eleggibilità non chiusa su Usare Potere/Mossa Esclusiva")
validity = ring.get("price_validity") or {}
if not re.search(r"realmente applicabili", str(validity.get("general", "")), re.I):
    fail("Risonanza: validità generale dei prezzi assente")
if not re.search(r"Velo 12", str(validity.get("world", "")), re.I):
    fail("Risonanza: limite Mondo a Velo 12 assente")
if not re.search(r"dadi finali", str(ring.get("natural_two_timing", "")), re.I):
    fail("Risonanza: timing del 2 naturale dopo Fato assente")
if not re.search(r"stessa risorsa", str(validity.get("general", "")), re.I):
    fail("Risonanza: regola sui costi aggiuntivi della stessa risorsa assente")
if not re.search(r"non parte", str(ring.get("price_procedure", "")), re.I) or not re.search(r"spesa anche se", str(ring.get("price_procedure", "")), re.I):
    fail("Risonanza: uso dopo prezzi non validi/rifiutati non normato")
if re.search(r"se il tavolo non usa", str((ring.get("prices") or {}).get("world", "")), re.I):
    fail("Risonanza: Mondo non deve avere fallback senza Velo Tracker")
if not re.search(r"eccezione.*categorie differenti", str(anchor.get("grounding", "")), re.I):
    fail("Ancora: edge case con secondo prezzo Legame non normato")

ring_sources = [
    ROOT / "chapters/05_come_si_gioca.md",
    ROOT / "chapters/30_quick_reference_giocatori.md",
    ROOT / "chapters/31_quick_reference_custode.md",
    ROOT / "products/quickstart/Mythic_Rings_Quickstart.md",
    ROOT / "products/player-kit/Mythic_Rings_Kit_del_Giocatore.md",
]
for path in ring_sources:
    text = path.read_text(encoding="utf-8")
    required_patterns = {
        "Risonanza": r"Risonanza dell'Anello",
        "6−→7–9": r"6−\s*(?:→|diventa)\s*7[–-]9",
        "7–9→10+": r"7[–-]9\s*(?:→|diventa)\s*10\+",
        "Corpo 4 PF": r"(?:Corpo[\s\S]{0,260}(?:4 PF|−4 PF)|(?:4 PF|−4 PF)[\s\S]{0,260}Corpo)",
        "Mondo/Velo": r"(?:Mondo[\s\S]{0,260}Velo|Velo[\s\S]{0,260}Mondo)",
        "eleggibilità chiusa": r"Mossa Esclusiva di Casata",
        "rifiuto consuma opportunità": r"(?:spes[ao]|speso).*anche se|anche se.*(?:rifiut|rinunc)",
    }
    for label, pattern in required_patterns.items():
        if not re.search(pattern, text, re.I):
            fail(f"{path.relative_to(ROOT)}: Ring Core incompleto ({label})")

# Il nome Ancora è riservato alla nuova regola, non alla capacità L3 di Amato.
for path in [ROOT / "chapters/04_creare_il_tuo_guardiano.md", ROOT / "chapters/05_come_si_gioca.md", ROOT / "products/player-kit/Mythic_Rings_Kit_del_Giocatore.md"]:
    text = path.read_text(encoding="utf-8")
    if re.search(r"\|\s*Amato\s*\|[^\n]*\*\*Ancora", text):
        fail(f"{path.relative_to(ROOT)}: collisione terminologica Ancora/Amato")

# Le quattro Casate sono stirpi di Anelli; non possono ricomparire come quattro soli artefatti milanesi.
lore_corpus = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in ["chapters/01_milano_nascosta.md", "chapters/02_i_custodi_e_gli_anelli_di_custodia.md"])
for pattern, label in [
    (r"quattro artefatti(?: magici)? leggendari", "quattro soli artefatti"),
    (r"Quelli di Milano\s+sono quattro", "quattro soli Anelli a Milano"),
]:
    if re.search(pattern, lore_corpus, re.I):
        fail(f"Lore Anelli incoerente: {label}")

# Parità delle distanze e rimozione di regole ad hoc residue.
quickstart_text = (ROOT / "products/quickstart/Mythic_Rings_Quickstart.md").read_text(encoding="utf-8")
kit_text = (ROOT / "products/player-kit/Mythic_Rings_Kit_del_Giocatore.md").read_text(encoding="utf-8")
for label, text in [("quickstart", quickstart_text), ("kit", kit_text)]:
    for band in ["Contatto", "Vicino", "Lontano", "Remoto"]:
        if not re.search(rf"\b{band}\b", text):
            fail(f"{label}: distanza canonica assente ({band})")
if re.search(r"\|\s*\*\*Medio\*\*\s*\|", quickstart_text):
    fail("quickstart: distanza Medio obsoleta")
if re.search(r"\*\*Medio\*\*\s*·", kit_text):
    fail("kit: distanza Medio obsoleta")

session_zero = (ROOT / "chapters/15_session_zero.md").read_text(encoding="utf-8")
if re.search(r"Punto Fato extra|\+1 forward al primo tiro", session_zero, re.I):
    fail("Sessione Zero: scaling gruppi piccoli viola i limiti canonici")

rings_chapter = (ROOT / "chapters/02_i_custodi_e_gli_anelli_di_custodia.md").read_text(encoding="utf-8")
if re.search(r"efficacia ridotta", rings_chapter, re.I):
    fail("Anelli: efficacia ridotta non quantificata")
if not (
    re.search(r"Separazione temporanea[\s\S]{0,500}non applica modificatori nascosti", rings_chapter, re.I)
    and re.search(r"Anello tolto[\s\S]{0,300}(?:Nessuna penalità numerica|non applica penalità numeriche)", rings_chapter, re.I)
):
    fail("Anelli: stati di rimozione/separazione senza regola esplicita")

one_shots = (ROOT / "chapters/28_tre_one_shot.md").read_text(encoding="utf-8")
if re.search(r"Ada Brambilla, custode notturna", one_shots, re.I):
    fail("Collisione terminologica Custode/occupazione in one-shot")

downtime_text = (ROOT / "chapters/23_le_12_attivita_di_downtime.md").read_text(encoding="utf-8")
if not re.search(r"Affrontare una Condizione dell'Anello durante il downtime", downtime_text, re.I):
    fail("Downtime: procedura di risoluzione Condizione dell'Anello assente")
if not re.search(r"beneficio numerico principale", downtime_text, re.I):
    fail("Downtime: la rimozione della Condizione non ha costo opportunità esplicito")

# Style guide: terminologia editoriale ad alto rischio.
style_guide = (ROOT / "docs/EDITORIAL_STYLE_GUIDE.md").read_text(encoding="utf-8")
if not re.search(r"Custode[^\n]*esclusivamente[^\n]*(?:GM|conduce il gioco)", style_guide, re.I):
    fail("Style guide: il singolare Custode non è riservato esplicitamente al GM")
if not re.search(r"Contatto, Vicino, Lontano, Remoto", style_guide, re.I):
    fail("Style guide: distanze canoniche non allineate")
if re.search(r"Distanze:\s*Vicino,\s*Medio,\s*Lontano,\s*Oltre", style_guide, re.I):
    fail("Style guide: vecchie distanze ancora normative")
if not re.search(r"Anello di Custodia\s*/\s*Anelli di Custodia", style_guide, re.I):
    fail("Style guide: grafia Anello di Custodia non fissata")

bestiary_text = (ROOT / "chapters/26_il_bestiario_di_milano.md").read_text(encoding="utf-8")
if re.search(r"custode funerario", bestiary_text, re.I):
    fail("Bestiario: Custode usato come personaggio in-fiction")

# Dimensioni anomale: avviso, non blocco.
for rel in meta["chapters"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    words = len(re.findall(r"\b\w+[’'\-]?\w*\b", text, re.UNICODE))
    if words > 9000:
        warn(f"Capitolo molto lungo: {rel} ({words} parole)")

for message in warnings:
    print(f"AVVISO: {message}")
if errors:
    for message in errors:
        print(f"ERRORE: {message}", file=sys.stderr)
    raise SystemExit(1)
print(f"Audit contenuti superato: {len(all_power_names)} poteri, {len(adversaries)} avversari, {len(meta['chapters'])} capitoli.")
