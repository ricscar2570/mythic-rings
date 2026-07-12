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
]:
    hits = re.findall(pattern, corpus, re.I)
    if hits:
        fail(f"Regola obsoleta rilevata ({label}): {len(hits)} occorrenze")

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
