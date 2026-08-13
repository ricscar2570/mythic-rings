#!/usr/bin/env python3
"""Controlla registri di governance della Fase 0."""
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUES = ROOT / "docs/project/ISSUE_REGISTER.csv"
DECISIONS = ROOT / "docs/project/DECISION_REGISTER.csv"
CHANGES = ROOT / "docs/project/CHANGELOG_MASTER.csv"

ALLOWED_PRIORITY = {"P0", "P1", "P2", "P3"}
ALLOWED_TYPES = {"defect", "design", "playtest", "style"}
ALLOWED_STATUS = {"open", "in_progress", "blocked", "closed", "accepted", "deferred"}
ALLOWED_CATEGORIES = {"canon", "rules", "balance", "text", "layout"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def valid_date(value: str) -> bool:
    try:
        dt.date.fromisoformat(value)
        return True
    except Exception:
        return False


def main() -> int:
    errors: list[str] = []
    issues = read_csv(ISSUES)
    decisions = read_csv(DECISIONS)
    changes = read_csv(CHANGES)

    ids: set[str] = set()
    roadmap_refs: set[str] = set()
    for row in issues:
        iid = row.get("issue_id", "").strip()
        if not iid:
            errors.append("issue senza issue_id")
            continue
        if iid in ids:
            errors.append(f"issue_id duplicato: {iid}")
        ids.add(iid)
        if row.get("priority") not in ALLOWED_PRIORITY:
            errors.append(f"{iid}: priority non valida {row.get('priority')!r}")
        if row.get("type") not in ALLOWED_TYPES:
            errors.append(f"{iid}: type non valido {row.get('type')!r}")
        if row.get("status") not in ALLOWED_STATUS:
            errors.append(f"{iid}: status non valido {row.get('status')!r}")
        if row.get("target_date") and not valid_date(row["target_date"]):
            errors.append(f"{iid}: target_date non ISO")
        if row.get("priority") == "P0":
            for field in ("owner", "target_date", "closure_criterion", "source_refs"):
                if not row.get(field, "").strip():
                    errors.append(f"{iid}: P0 senza {field}")
        ref = row.get("roadmap_ref", "").strip()
        if ref:
            if ref in roadmap_refs:
                errors.append(f"roadmap_ref duplicato senza merge esplicito: {ref}")
            roadmap_refs.add(ref)

    dids: set[str] = set()
    for row in decisions:
        did = row.get("decision_id", "").strip()
        if not did:
            errors.append("decisione senza ID")
            continue
        if did in dids:
            errors.append(f"decision_id duplicato: {did}")
        dids.add(did)
        for field in ("status", "owner", "due_date", "gate", "question"):
            if not row.get(field, "").strip():
                errors.append(f"{did}: campo obbligatorio vuoto {field}")
        if row.get("due_date") and not valid_date(row["due_date"]):
            errors.append(f"{did}: due_date non ISO")

    cids: set[str] = set()
    seen_categories: set[str] = set()
    for row in changes:
        cid = row.get("change_id", "").strip()
        if not cid:
            errors.append("changelog master: riga senza change_id")
            continue
        if cid in cids:
            errors.append(f"change_id duplicato: {cid}")
        cids.add(cid)
        cat = row.get("category", "")
        if cat not in ALLOWED_CATEGORIES:
            errors.append(f"{cid}: category non valida {cat!r}")
        seen_categories.add(cat)
        if not row.get("summary", "").strip() or not row.get("evidence", "").strip():
            errors.append(f"{cid}: summary/evidence mancanti")
    missing_categories = ALLOWED_CATEGORIES - seen_categories
    if missing_categories:
        errors.append(f"changelog master senza categorie richieste: {sorted(missing_categories)}")

    expected_roadmap = {f"P0-{i:02d}" for i in range(1, 8)} | {f"P1-{i:02d}" for i in range(1, 9)}
    missing_refs = expected_roadmap - roadmap_refs
    if missing_refs:
        errors.append(f"backlog del piano non importato: {sorted(missing_refs)}")

    if errors:
        print("Governance NON valida:")
        for e in errors:
            print(f"- {e}")
        return 1

    p0 = sum(1 for r in issues if r["priority"] == "P0")
    print("Governance valida.")
    print(f"  issue: {len(issues)} (P0: {p0})")
    accepted = sum(1 for r in decisions if r.get("status") == "accepted")
    open_decisions = sum(1 for r in decisions if r.get("status") == "open")
    print(f"  decisioni registrate: {len(decisions)} (accepted: {accepted}, open: {open_decisions})")
    print(f"  changelog master: {len(changes)} voci / 5 categorie")
    print("  P0 con owner, target date, fonte e criterio di chiusura: sì")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
