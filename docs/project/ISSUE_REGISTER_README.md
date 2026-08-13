# Registro delle criticità e delle decisioni

Questa cartella chiude **P0.2 — Costruire il registro delle criticità**.

## File proprietari

- `ISSUE_REGISTER.csv`: backlog unico di difetti, scelte di design, domande di playtest e preferenze/stile.
- `DECISION_REGISTER.csv`: decisioni aperte che richiedono una scelta del lead designer.
- `CHANGELOG_MASTER.csv`: registro strutturato delle modifiche per categoria `canon`, `rules`, `balance`, `text`, `layout`.
- `ID_CONVENTIONS.md`: regole per ID stabili di regole, poteri, PNG, luoghi, creature, issue e decisioni.

## Campi chiave delle issue

- `issue_id`: ID stabile di categoria.
- `roadmap_ref`: riferimento all'ID del piano (`P0-01`, `P1-03` ecc.).
- `priority`: severità/urgenza `P0`–`P3`.
- `type`: `defect`, `design`, `playtest`, `style`.
- `status`: `open`, `in_progress`, `blocked`, `closed`, `accepted`, `deferred`.
- `owner`: una sola funzione accountable.
- `target_date`: data obiettivo ISO `YYYY-MM-DD`.
- `dependencies`: ID separati da `;`.
- `decision`: decisione adottata, vuota finché aperta.
- `closure_criterion`: prova verificabile necessaria per chiudere.
- `source_refs`: riferimenti al piano o ad altre evidenze.
- `merged_refs`: ID/alias assorbiti; non cancellare i riferimenti dei duplicati.

## Regole operative

1. Nessun P0 può restare senza owner, data obiettivo e criterio di chiusura.
2. Una preferenza non diventa difetto senza un obiettivo esplicito.
3. Una domanda da misurare resta `playtest` finché non esistono dati.
4. I duplicati vengono uniti mantenendo in `merged_refs` gli ID precedenti.
5. Ogni chiusura deve compilare `decision` ed evidenza verificabile nel criterio di chiusura o nel report di gate.
6. Le modifiche normative significative continuano a richiedere un ADR in `docs/decisions/`.

Controllo automatico:

```bash
python3 scripts/validate_project_governance.py
```
