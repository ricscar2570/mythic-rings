# Mythic Rings 0.9.3-beta.9 — Source / Artifact Alignment

**Source snapshot commit:** `96ad431138d7370fd4a8d8d83192b32da98efe90`  
**Source release path:** `sources/releases/0.9.3-beta.9/`

## Two beta.9 PDF hashes

The source snapshot was reconstructed from the beta.9 PDF with SHA-256:

`93cc50ccbcbbf270ba4340619072729f40b48a9da7356a38c6e92d812a16fcf7`

The beta.9 PDF delivered for the independent editorial read has SHA-256:

`2fa92748d0b11a0de246b758812e6cb0aaaf4a21e0d782edcfe2ba8cc8f1e193`

Both contain **387 pages**.

## Equivalence check

A page-by-page text extraction comparison was run across all 387 pages.

**Result: 0 changed text pages.**

The source snapshot therefore represents the same beta.9 editorial corpus as the delivered external-read candidate. The different PDF hashes come from byte-level PDF assembly / metadata / object differences, not from different rule or manuscript text.

## Provenance rule

Do not rewrite the immutable source snapshot only to make its historical reference hash equal the later assembled artifact hash.

Instead:

- use `sources/releases/0.9.3-beta.9/` as the beta.9 textual source checkpoint;
- use the delivered PDF SHA `2fa92748...` when identifying the external-read artifact;
- preserve the earlier `93cc50...` reference inside the source snapshot as provenance of the extraction point;
- any future source normalization must compare against the beta.9 textual corpus and the accepted post-read artifact.

## Reconstructible archive

The complete 48-file source snapshot is stored in:

`sources/releases/0.9.3-beta.9/snapshot_parts/part-00.b64` … `part-17.b64`

Run:

`python sources/releases/0.9.3-beta.9/reconstruct_source_snapshot.py`

Expected reconstructed ZIP SHA-256:

`ef9ddd10169c44892b86dca54c9b9a0e5a3f52e8e710ff173394e5acf4781ad1`

Expected ZIP size: **256120 bytes**.  
Expected ZIP files: **48**.
