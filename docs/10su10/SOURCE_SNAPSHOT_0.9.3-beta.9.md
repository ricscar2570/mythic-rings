# Source snapshot — Mythic Rings 0.9.3-beta.9

This checkpoint stores the **recoverable source snapshot** corresponding to the current
`0.9.3-beta.9 BLIND CLEAN CANDIDATE`.

## Location

`sources/releases/0.9.3-beta.9/`

The directory contains the readable metadata/pipeline and an exact ZIP source snapshot
encoded into 18 Base64 parts under `snapshot_parts/`.

Reconstruct it with:

```bash
cd sources/releases/0.9.3-beta.9
python reconstruct_source_snapshot.py
```

Expected ZIP SHA-256:

`ef9ddd10169c44892b86dca54c9b9a0e5a3f52e8e710ff173394e5acf4781ad1`

The reconstructed ZIP contains **48 source files**, including all 33 reconstructed chapter
Markdown files, front matter, beta.9 book manifest, final acceptance checklist, appendix text,
checksums and the Python editorial pipeline.

## Provenance

The legacy repository root `chapters/` belongs to the earlier beta.2 native source line.
It has deliberately **not** been overwritten, because it did not generate beta.9.

Beta.9 was produced by successive editorial rebuilds of the PDF artifact. The versioned
snapshot therefore records the beta.9 textual corpus reconstructed from the candidate PDF
plus the actual scripts used to finalize it. This is the honest restart point for migrating
beta.9 back into the native Markdown/data build after the independent second-read gate.

## Artifact identity

The source-sync snapshot references the beta.9 candidate present at sync time:

- 387 pages
- reference PDF SHA-256:
  `93cc50ccbcbbf270ba4340619072729f40b48a9da7356a38c6e92d812a16fcf7`

Earlier beta.9 checkpoint notes may reference an intermediate candidate hash. This source
snapshot is the authoritative identity for source-reconstruction purposes; it does **not**
promote the candidate to final blind-ready status.

Independent second read remains pending.
