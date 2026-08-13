# Baseline immutabile — Mythic Rings 0.9.0-beta.2 Ring Core

Questa cartella chiude **P0.1 — Congelare la baseline** del piano di sviluppo.

- `source_snapshot.tar.gz` contiene lo stato sorgente della beta 0.9.0-beta.2 **prima** dell'introduzione dei file di governance della Fase 0.
- `BASELINE.json` registra versione, data di cattura, numero di file, checksum dello snapshot e identificazione del manuale PDF di riferimento.
- Il PDF di riferimento non viene duplicato nella repository per evitare di versionare un artefatto derivato; il suo SHA-256 e il numero di pagine rendono però verificabile quale artefatto costituisce la baseline.

## Regola di immutabilità

Questi file non vanno modificati. Se una baseline futura deve essere congelata, creare una nuova directory sotto `archive/baselines/<versione>/`.

Verifica:

```bash
python3 scripts/verify_baseline.py
```
