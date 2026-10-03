# Mythic Rings 0.9.3-beta.9 — Source Snapshot

This directory is the source checkpoint corresponding to the **0.9.3-beta.9 BLIND CLEAN CANDIDATE**.

## Reference

- PDF: `Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf`
- SHA-256: `93cc50ccbcbbf270ba4340619072729f40b48a9da7356a38c6e92d812a16fcf7`
- Pages: 387

## What is here

- `frontmatter.md`: reconstructed front matter text.
- `chapters/`: chapter-by-chapter textual snapshot extracted from the final beta.9 PDF.
- `pipeline/`: the actual Python scripts used to rebuild/finalize beta.9 pages, appendices, Unicode ranges, metadata and outline.
- `audit/CHECKLIST_OPERATIVA_BETA8.txt`: the acceptance checklist used for the final editorial pass.
- `book.yml`: beta.9 manifest aligned to this snapshot.
- `SOURCE_MANIFEST.yml`: provenance, limitations and checksums.

## Important provenance note

The repository's historical root `chapters/` tree comes from the earlier beta.2 native build and **must not be represented as having generated beta.9**. Beta.9 was reached through successive editorial rebuilds of the PDF artifact. This directory therefore records the actual beta.9 textual state plus the real transformation pipeline. It is the correct restart point for future source normalization.

## Recommended next source step

After the independent second-read gate, migrate this snapshot into the repository's native Markdown/data build, chapter by chapter, and verify that a clean build reproduces the approved beta.9+ textual corpus before deleting this compatibility snapshot.
