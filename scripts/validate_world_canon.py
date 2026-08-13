#!/usr/bin/env python3
"""Gate G1: verifica il canon di mondo della beta Ring Core.

Il controllo è intenzionalmente conservativo: non prova a validare l'intera
ambientazione, ma impedisce la regressione dei P0 CANON-001..004 chiusi in G1.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data/canon"
CH = ROOT / "chapters"
PRODUCTS = ROOT / "products"


def load_yaml(name: str):
    with (CANON / name).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def user_facing_text() -> str:
    parts: list[str] = []
    for base in (CH, PRODUCTS):
        for p in sorted(base.rglob("*.md")):
            parts.append(f"\n<!-- {p.relative_to(ROOT)} -->\n")
            parts.append(read(p))
    return "\n".join(parts)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    world = load_yaml("world.yml")
    geo = load_yaml("occult_geography.yml")
    npcs = load_yaml("npcs.yml")
    timeline = load_yaml("timeline.yml")

    # --- struttura minima -------------------------------------------------
    if world.get("setting", {}).get("temporal_mode") != "presente_mobile":
        errors.append("world.yml: temporal_mode deve essere presente_mobile in G1")
    if world.get("setting", {}).get("display_phrase") != "Milano, oggi":
        errors.append("world.yml: display phrase canonica deve essere 'Milano, oggi'")

    lines = geo.get("lines") or []
    secondaries = geo.get("secondary_nexus") or []
    if len(lines) != 5:
        errors.append(f"occult_geography.yml: attese 5 Linee, trovate {len(lines)}")
    if len(secondaries) != 5:
        errors.append(f"occult_geography.yml: attesi 5 Nexus Secondari, trovati {len(secondaries)}")
    if geo.get("policy", {}).get("numeric_roll_modifiers") is not False:
        errors.append("occult_geography.yml: numeric_roll_modifiers deve essere false")

    line_ids = [x.get("id") for x in lines]
    if len(line_ids) != len(set(line_ids)):
        errors.append("occult_geography.yml: ID Linea duplicati")
    if line_ids != [f"MR-LEY-{i:03d}" for i in range(1, 6)]:
        errors.append(f"occult_geography.yml: ID Linea inattesi {line_ids}")

    sec_ids = [x.get("id") for x in secondaries]
    if len(sec_ids) != len(set(sec_ids)):
        errors.append("occult_geography.yml: ID Nexus Secondario duplicati")
    if sec_ids != [f"MR-LOC-{i:03d}" for i in range(2, 7)]:
        errors.append(f"occult_geography.yml: ID Nexus inattesi {sec_ids}")

    for node in secondaries:
        if node.get("line") not in set(line_ids):
            errors.append(f"{node.get('id')}: Linea inesistente {node.get('line')}")
        for field in ("function", "steward", "risk", "benefit", "sensory_signal"):
            if not str(node.get(field, "")).strip():
                errors.append(f"{node.get('id')}: campo vuoto {field}")

    expected_routes = {
        "MR-LEY-001": ["Sesto San Giovanni", "Loreto", "Porta Venezia", "San Babila", "Duomo"],
        "MR-LEY-002": ["Navigli", "Darsena", "Porta Ticinese", "Colonne di San Lorenzo", "Duomo"],
        "MR-LEY-003": ["Parco Sempione", "Castello Sforzesco", "Cairoli", "Duomo"],
        "MR-LEY-004": ["Cimitero Monumentale", "Porta Garibaldi", "Brera", "Duomo"],
        "MR-LEY-005": ["Porta Romana", "Crocetta", "Duomo"],
    }
    for line in lines:
        if line.get("route") != expected_routes.get(line.get("id")):
            errors.append(f"{line.get('id')}: percorso divergente dal canon G1")

    central = geo.get("central_nexus", {})
    if central.get("id") != "MR-LOC-001" or central.get("name") != "Nexus del Duomo":
        errors.append("Nexus centrale non canonico")
    if central.get("lines") != line_ids:
        errors.append("Nexus del Duomo: convergenza non coincide con le 5 Linee")

    # --- roster ------------------------------------------------------------
    roster = npcs.get("npcs") or []
    by_id = {n.get("id"): n for n in roster}
    if len(roster) != 7 or len(by_id) != 7:
        errors.append(f"npcs.yml: attesi 7 PNG canonici unici, trovati {len(roster)}")
    expected_names = {
        "MR-NPC-001": "Elisabetta Conti",
        "MR-NPC-002": "Eleonora Visconti",
        "MR-NPC-003": "Leila Ferrara",
        "MR-NPC-004": "Kwame Asante",
        "MR-NPC-005": "Marisol Reyes",
        "MR-NPC-006": "Padre Tommaso De Luca",
        "MR-NPC-007": "Valentina Riva",
    }
    for iid, name in expected_names.items():
        if by_id.get(iid, {}).get("name") != name:
            errors.append(f"{iid}: nome canonico mancante/divergente")

    # --- timeline ----------------------------------------------------------
    events = timeline.get("events") or []
    if not (12 <= len(events) <= 20):
        errors.append(f"timeline.yml: attesi 12-20 eventi, trovati {len(events)}")
    tids = [e.get("id") for e in events]
    if len(tids) != len(set(tids)):
        errors.append("timeline.yml: ID duplicati")
    joined_timeline = "\n".join(str(e.get("event", "")) for e in events)
    if "protocolli permanenti per il Monumentale" in joined_timeline:
        errors.append("timeline.yml: il Monumentale non può comparire come istituzione del 1630")
    if "tradizioni yoruba o nahua/mesoamericane derivino da Milano" not in "\n".join(timeline.get("principles") or []):
        errors.append("timeline.yml: manca il principio di separazione dalle tradizioni reali")

    # --- governance di Gate G1 --------------------------------------------
    with (ROOT / "docs/project/DECISION_REGISTER.csv").open(encoding="utf-8", newline="") as f:
        decisions = list(csv.DictReader(f))
    g1_decisions = [d for d in decisions if d.get("gate") == "G1"]
    if len(g1_decisions) != 8:
        errors.append(f"governance: attese 8 decisioni G1, trovate {len(g1_decisions)}")
    for d in g1_decisions:
        if d.get("status") != "accepted":
            errors.append(f"{d.get('decision_id')}: decisione G1 non accepted ({d.get('status')})")
        if not d.get("decision", "").strip() or not d.get("evidence", "").strip():
            errors.append(f"{d.get('decision_id')}: decision/evidence mancanti")

    with (ROOT / "docs/project/ISSUE_REGISTER.csv").open(encoding="utf-8", newline="") as f:
        issues = {r.get("issue_id"): r for r in csv.DictReader(f)}
    for iid in ("CANON-001", "CANON-002", "CANON-003", "CANON-004"):
        if issues.get(iid, {}).get("status") != "closed":
            errors.append(f"{iid}: P0 canon non chiuso")

    # --- corpus user-facing ------------------------------------------------
    corpus = user_facing_text()
    forbidden = {
        "Milano, 2025": "data fissa obsoleta",
        "Tre milioni e mezzo di persone": "scala demografica obsoleta",
        "10 milioni nell’area metropolitana": "scala amministrativa errata",
        "10 milioni nell'area metropolitana": "scala amministrativa errata",
        "devastata dalle guerre di Federico II": "formulazione storica respinta",
        "arrivò a Milano nel Seicento con i mercanti": "storia culturale inventata respinta",
        "Arrivò a Milano nell’Ottocento attraverso l’immigrazione": "storia culturale inventata respinta",
        "Arrivò a Milano nell'Ottocento attraverso l'immigrazione": "storia culturale inventata respinta",
        "Caffè Fiorio": "luogo reale di Torino usato come se fosse a Brera",
        "fictionally": "anglicismo residuo",
    }
    for needle, why in forbidden.items():
        if needle.casefold() in corpus.casefold():
            errors.append(f"corpus: trovato {needle!r} ({why})")

    # Linee canoniche devono apparire nelle viste principali. Il capitolo 3
    # le espone in prosa, mentre 1 e 11 usano tabelle: verifichiamo quindi
    # l'ordine dei waypoint, non una specifica punteggiatura.
    def ordered_waypoints(text: str, waypoints: list[str]) -> bool:
        text = re.sub(r"\s+", " ", text)
        pos = -1
        for waypoint in waypoints:
            waypoint = re.sub(r"\s+", " ", waypoint)
            nxt = text.find(waypoint, pos + 1)
            if nxt < 0:
                return False
            pos = nxt
        return True

    ch1_lines = read(ROOT / "chapters/01_milano_nascosta.md")
    ch3_lines = read(ROOT / "chapters/03_le_quattro_casate.md")
    ch11_lines = read(ROOT / "chapters/11_la_milano_sotterranea.md")
    for line in lines:
        route = " → ".join(line["route"])
        if line.get("name") not in ch1_lines or route not in ch1_lines:
            errors.append(f"capitolo 1: {line.get('name')} o percorso non canonico/mancante")
        if line.get("id") not in ch11_lines or route not in ch11_lines:
            errors.append(f"capitolo 11: {line.get('id')} o percorso non canonico/mancante")
        if line.get("affinity"):
            if line.get("name") not in ch3_lines or not ordered_waypoints(ch3_lines[ch3_lines.find(line.get("name")):], line["route"]):
                errors.append(f"capitolo 3: {line.get('name')} o waypoint non canonici/mancanti")

    # Policy meccanica deve essere esplicita nelle fonti esposte.
    ch11 = read(CH / "11_la_milano_sotterranea.md")
    if "Non concede +1" not in ch11 or "non riduce" not in ch11:
        errors.append("capitolo 11: politica non numerica di Linee/Nexus non sufficientemente esplicita")

    # P0-06: vecchi pacchetti locali noti non possono rientrare.
    ch12 = read(CH / "12_i_dodici_quartieri_di_milano.md")
    obsolete_local_patterns = [
        r"espresso che dà \+1",
        r"ottenere \+2 a un tiro di Investigare",
        r"Un rituale condotto tra le colonne ha \+1",
        r"recupera 1d4 PF extra",
        r"recupera 1d6 PF",
        r"\+1 a poteri Ife",
        r"\+1d6 PF al risveglio",
        r"rimuove 1 condizione negativa o 2 Stress",
        r"Parlare con Morti con \+1",
        r"Leggere Situazione con \+2",
        r"\+1 a Leggere Situazione per minacce attive",
        r"\+1 Armatura temporanea",
        r"pozioni curative \(1d4 PF",
        r"\+1 a qualsiasi tiro che coinvolga emozioni",
        r"-1 Stress ma anche -1d4 PF",
        r"attingere.{0,40}\+1 a un tiro",
    ]
    for pat in obsolete_local_patterns:
        if re.search(pat, ch12, flags=re.IGNORECASE | re.DOTALL):
            errors.append(f"capitolo 12: possibile regola locale obsoleta /{pat}/")

    # Roster testuale minimo.
    ch2 = read(CH / "02_i_custodi_e_gli_anelli_di_custodia.md")
    required_ch2 = [
        "Presidente — Dottoressa Elisabetta Conti",
        "Anziana Avalon — Professoressa Eleonora Visconti",
        "Anziana Umbra — Leila Ferrara",
        "Anziano Ife — Professor Kwame Asante",
        "Anziana Mictlan — Signora Marisol Reyes",
        "Padre Tommaso De Luca",
        "non occupa un seggio",
    ]
    for needle in required_ch2:
        if needle not in ch2:
            errors.append(f"capitolo 2: roster canonico incompleto, manca {needle!r}")

    ch13 = read(CH / "13_le_fazioni_di_milano.md")
    for needle in ("40 Guardiani attivi", "200 persone di supporto", "circa 100 operativi", "Presidente neutrale"):
        if needle not in ch13:
            errors.append(f"capitolo 13: numeri/istituzioni non canonici, manca {needle!r}")

    # I PNG canonici non devono tornare a essere pregenerati o esempi PG.
    pregens = read(CH / "04_creare_il_tuo_guardiano.md") + "\n" + read(PRODUCTS / "quickstart/Mythic_Rings_Quickstart.md")
    for name in ("Leila Ferrara", "Kwame Asante", "Marisol Reyes", "Valentina Riva"):
        # nomi potrebbero apparire come NPC nell'avventura, ma non nei blocchi pregenerati di questi due file.
        if name in pregens:
            errors.append(f"pregenerati: PNG canonico riutilizzato come PG: {name}")

    # Numeri civici canonici nel capitolo di apertura.
    ch1 = read(CH / "01_milano_nascosta.md")
    for needle in ("Milano, oggi", "circa 1,4 milioni", "circa 3,25 milioni"):
        if needle.casefold() not in ch1.casefold():
            errors.append(f"capitolo 1: manca {needle!r}")

    if errors:
        print("Gate G1 — canon NON valido:")
        for e in errors:
            print(f"- ERRORE: {e}")
        for w in warnings:
            print(f"- AVVISO: {w}")
        return 1

    print("Gate G1 — canon valido.")
    print(f"  Linee Ley: {len(lines)}")
    print(f"  Nexus: 1 centrale + {len(secondaries)} secondari")
    print(f"  PNG ricorrenti canonici: {len(roster)}")
    print(f"  Cronologia: {len(events)} eventi")
    print("  Bonus locali generici Linee/Nexus: vietati e non rilevati")
    print("  Formulazioni storiche/culturali P0 obsolete: non rilevate nel corpus user-facing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
