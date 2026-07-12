#!/usr/bin/env python3
"""Pipeline PDF deterministica per Mythic Rings.

Modalità ``once``:
- converte il DOCX già costruito usando il lock di paginazione;
- estrae le pagine effettive dei capitoli;
- rifiuta la build se il lock è diventato obsoleto;
- applica metadati e segnalibri in modo atomico.

Modalità ``refresh``:
- rigenera il lock di paginazione con passaggi successivi;
- termina quando due mappe consecutive coincidono;
- salva il lock stabile e produce il PDF definitivo.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
META = yaml.safe_load((ROOT / "book.yml").read_text(encoding="utf-8"))
LOCK = ROOT / "data" / "toc-pages.lock.json"
EXTRACTOR = ROOT / "build" / "extract_toc_pages.py"
POSTPROCESS = ROOT / "build" / "postprocess_pdf.py"
ENGINE = ROOT / "build" / "engine.js"


def run(cmd: list[str], *, timeout: int, env: dict[str, str] | None = None) -> str:
    """Run a command with bounded process-group termination and file-backed logs."""
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as log:
        proc = subprocess.Popen(
            cmd,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        timed_out = False
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                code = proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    code = proc.wait(timeout=10)
                except subprocess.TimeoutExpired as exc:
                    raise RuntimeError(f"Impossibile terminare: {' '.join(cmd)}") from exc
        log.flush()
        log.seek(0)
        output = log.read()
    if timed_out:
        raise RuntimeError(f"Comando scaduto dopo {timeout}s: {' '.join(cmd)}\n{output}")
    if code:
        raise RuntimeError(f"Comando fallito ({code}): {' '.join(cmd)}\n{output}")
    return output


def find_libreoffice() -> str:
    for candidate in ("libreoffice", "soffice"):
        found = shutil.which(candidate)
        if found:
            return found
    raise RuntimeError("LibreOffice non trovato")


def convert(docx: Path, pdf: Path, dist: Path, pass_name: str) -> None:
    if pdf.exists():
        pdf.unlink()
    profile = Path(tempfile.mkdtemp(prefix=f"mythic-rings-{pass_name}-", dir="/tmp"))
    try:
        output = run(
            [
                find_libreoffice(),
                f"-env:UserInstallation={profile.as_uri()}",
                "--headless",
                "--nologo",
                "--nodefault",
                "--nolockcheck",
                "--nofirststartwizard",
                "--convert-to",
                "pdf",
                "--outdir",
                str(dist),
                str(docx),
            ],
            timeout=1200,
        )
        if output.strip():
            print(output.strip(), flush=True)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise RuntimeError(f"LibreOffice non ha prodotto un PDF valido: {pdf}")


def extract(pdf: Path, destination: Path) -> dict[str, int]:
    output = run([sys.executable, str(EXTRACTOR), str(pdf), str(destination)], timeout=180)
    if output.strip():
        print(output.strip(), flush=True)
    return json.loads(destination.read_text(encoding="utf-8"))


def normalized(mapping: dict[str, int]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(mapping.items())}


def differences(expected: dict[str, int], actual: dict[str, int]) -> list[str]:
    lines: list[str] = []
    for key in sorted(set(expected) | set(actual)):
        if expected.get(key) != actual.get(key):
            lines.append(f"{key}: lock={expected.get(key)!r}, effettiva={actual.get(key)!r}")
    return lines


def rebuild_docx(dist: Path, toc_path: Path) -> None:
    env = dict(os.environ)
    env["MYTHIC_TOC_PAGES"] = str(toc_path)
    output = run(
        ["node", str(ENGINE), str(ROOT / "chapters"), str(dist)],
        timeout=600,
        env=env,
    )
    if output.strip():
        print(output.strip(), flush=True)


def postprocess(pdf: Path) -> None:
    output = run([sys.executable, str(POSTPROCESS), str(pdf)], timeout=180)
    if output.strip():
        print(output.strip(), flush=True)


def build_once(dist: Path) -> None:
    if not LOCK.exists():
        raise RuntimeError(
            f"Lock di paginazione assente: {LOCK}. Eseguire npm run build:pdf:refresh."
        )
    expected = normalized(json.loads(LOCK.read_text(encoding="utf-8")))
    docx = dist / f"{META['output_basename']}.docx"
    pdf = dist / f"{META['output_basename']}.pdf"
    if not docx.exists():
        raise RuntimeError(f"DOCX non trovato: {docx}")

    print("Build PDF verificata a un passaggio", flush=True)
    convert(docx, pdf, dist, "single")
    actual_path = dist / "toc-pages.json"
    actual = normalized(extract(pdf, actual_path))
    delta = differences(expected, actual)
    if delta:
        preview = "\n".join(f"  - {line}" for line in delta[:20])
        raise RuntimeError(
            "Il lock di paginazione non coincide con il PDF prodotto. "
            "Eseguire npm run build:pdf:refresh.\n" + preview
        )
    postprocess(pdf)
    print(
        f"PDF verificato: {pdf} ({pdf.stat().st_size // 1024} KB); "
        f"indice stabile su {len(META['chapters'])} capitoli.",
        flush=True,
    )


def refresh(dist: Path) -> None:
    docx = dist / f"{META['output_basename']}.docx"
    pdf = dist / f"{META['output_basename']}.pdf"
    if not docx.exists():
        raise RuntimeError(f"DOCX non trovato: {docx}")

    print("Rigenerazione del lock di paginazione", flush=True)
    current_map: dict[str, int] | None = None
    stable_path: Path | None = None

    for iteration in range(1, 4):
        convert(docx, pdf, dist, f"refresh-{iteration}")
        map_path = dist / f"toc-pages-pass{iteration}.json"
        new_map = normalized(extract(pdf, map_path))
        if current_map is not None and new_map == current_map:
            stable_path = map_path
            print(f"Paginazione stabilizzata al passaggio {iteration}.", flush=True)
            break
        current_map = new_map
        rebuild_docx(dist, map_path)
    else:
        raise RuntimeError("La paginazione non si è stabilizzata entro tre passaggi")

    assert stable_path is not None
    stable = normalized(json.loads(stable_path.read_text(encoding="utf-8")))
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps(stable, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dist / "toc-pages.json").write_text(
        json.dumps(stable, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    postprocess(pdf)
    print(f"Lock aggiornato: {LOCK}", flush=True)
    print(f"PDF definitivo: {pdf} ({pdf.stat().st_size // 1024} KB)", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("once", "refresh"))
    parser.add_argument("dist", nargs="?", default=str(ROOT / "dist"))
    args = parser.parse_args()
    dist = Path(args.dist).resolve()
    dist.mkdir(parents=True, exist_ok=True)
    if args.mode == "once":
        build_once(dist)
    else:
        refresh(dist)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRORE: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
