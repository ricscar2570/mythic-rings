#!/usr/bin/env python3
"""Valida un bundle JSON di playtest Mythic Rings senza dipendenze esterne."""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs/playtest/schema/session_bundle.schema.json"


def fail(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def validate_schema(value: Any, schema: dict[str, Any], path: str, errors: list[str]) -> None:
    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]
        if not any(type_matches(value, t) for t in allowed):
            fail(errors, path, f"tipo {type(value).__name__} non ammesso; atteso {allowed}")
            return

    if "const" in schema and value != schema["const"]:
        fail(errors, path, f"valore {value!r} diverso da const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        fail(errors, path, f"valore {value!r} non in {schema['enum']}")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            fail(errors, path, f"lunghezza < {schema['minLength']}")
        if "pattern" in schema and not re.match(schema["pattern"], value):
            fail(errors, path, f"non rispetta pattern {schema['pattern']}")

    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            fail(errors, path, f"{value} < minimo {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            fail(errors, path, f"{value} > massimo {schema['maximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            fail(errors, path, f"numero elementi {len(value)} < {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for idx, item in enumerate(value):
                validate_schema(item, item_schema, f"{path}[{idx}]", errors)

    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                fail(errors, path, f"campo obbligatorio assente: {req}")
        props = schema.get("properties", {})
        for key, child in value.items():
            if key in props:
                validate_schema(child, props[key], f"{path}.{key}", errors)
            elif schema.get("additionalProperties") is False:
                fail(errors, path, f"campo non previsto: {key}")


def cross_validate(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    session = data.get("session", {})
    sid = session.get("session_id", "")
    gid = session.get("group_id", "")
    if sid and gid and not sid.startswith(gid + "-"):
        fail(errors, "$.session", "session_id non appartiene al group_id")

    characters = data.get("characters", [])
    char_ids = {c.get("character_id") for c in characters}
    if len(char_ids) != len(characters):
        fail(errors, "$.characters", "character_id duplicato")
    for cid in char_ids:
        if cid and gid and not cid.startswith(gid + "-"):
            fail(errors, "$.characters", f"{cid} non appartiene a {gid}")
    if session.get("players_count") is not None and len(characters) != session.get("players_count"):
        fail(errors, "$.characters", "il numero di personaggi deve coincidere con players_count nel modello v1")

    event_ids: set[str] = set()
    decision_times: list[int] = []
    for i, e in enumerate(data.get("resonance_events", [])):
        p = f"$.resonance_events[{i}]"
        eid = e.get("event_id")
        if eid in event_ids:
            fail(errors, p, f"event_id duplicato: {eid}")
        event_ids.add(eid)
        if e.get("character_id") not in char_ids:
            fail(errors, p, "character_id non presente nella sessione")
        if sid and not str(e.get("scene_id", "")).startswith(sid + "-"):
            fail(errors, p, "scene_id non appartiene alla sessione")

        started = e.get("procedure_started")
        spent = e.get("opportunity_spent")
        valid1, valid2 = e.get("price_1_valid"), e.get("price_2_valid")
        c1, c2 = e.get("price_1_category"), e.get("price_2_category")
        choice = e.get("choice")
        pre, post = e.get("pre_result"), e.get("post_result")
        anchor = e.get("anchor_used")

        if started:
            if not (valid1 and valid2):
                fail(errors, p, "procedure_started richiede due prezzi validi")
            if not spent:
                fail(errors, p, "dopo due prezzi validi l'opportunità deve risultare spesa")
            if c1 == c2 and not (anchor and c1 == "Legame"):
                fail(errors, p, "i prezzi devono avere categorie differenti salvo eccezione Ancora/Legame")
        else:
            if spent:
                fail(errors, p, "una procedura non iniziata non può spendere l'opportunità")
            if choice != "rifiuto" or post != pre:
                fail(errors, p, "procedura non iniziata: scelta rifiuto e risultato invariato")

        if choice == "rifiuto":
            if post != pre:
                fail(errors, p, "rifiuto: il risultato deve restare invariato")
        else:
            if choice not in {c1, c2}:
                fail(errors, p, "la scelta deve corrispondere a uno dei prezzi offerti")
            expected = "7-9" if pre == "6-" else "10+" if pre == "7-9" else None
            if expected and post != expected:
                fail(errors, p, f"Risonanza accettata: atteso {expected}, trovato {post}")
        if isinstance(e.get("decision_seconds"), int):
            decision_times.append(e["decision_seconds"])

    combat_keys: set[tuple[str, int]] = set()
    for i, r in enumerate(data.get("combat_rounds", [])):
        p = f"$.combat_rounds[{i}]"
        if sid and not str(r.get("combat_id", "")).startswith(sid + "-"):
            fail(errors, p, "combat_id non appartiene alla sessione")
        key = (r.get("combat_id"), r.get("round_number"))
        if key in combat_keys:
            fail(errors, p, "round duplicato nello stesso combattimento")
        combat_keys.add(key)

    lookup_ids: set[str] = set()
    lookup_times: list[int] = []
    for i, l in enumerate(data.get("rule_lookups", [])):
        p = f"$.rule_lookups[{i}]"
        lid = l.get("lookup_id")
        if lid in lookup_ids:
            fail(errors, p, f"lookup_id duplicato: {lid}")
        lookup_ids.add(lid)
        if isinstance(l.get("elapsed_seconds"), int):
            lookup_times.append(l["elapsed_seconds"])

    ps = data.get("post_session", {})
    yes = ps.get("second_session_yes_count", 0)
    no = ps.get("second_session_no_count", 0)
    if session.get("players_count") is not None and yes + no != session.get("players_count"):
        fail(errors, "$.post_session", "yes + no sulla seconda sessione deve coincidere con players_count")

    return {
        "session_id": sid,
        "characters": len(characters),
        "resonance_events": len(data.get("resonance_events", [])),
        "combat_rounds": len(data.get("combat_rounds", [])),
        "rule_lookups": len(data.get("rule_lookups", [])),
        "issues": len(data.get("issues", [])),
        "median_resonance_decision_seconds": statistics.median(decision_times) if decision_times else None,
        "median_rule_lookup_seconds": statistics.median(lookup_times) if lookup_times else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", type=Path)
    args = ap.parse_args()
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        data = json.loads(args.bundle.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERRORE: impossibile leggere schema/bundle: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    validate_schema(data, schema, "$", errors)
    summary = cross_validate(data, errors) if isinstance(data, dict) else {}
    if errors:
        print("Playtest dataset NON valido:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Playtest dataset valido.")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
