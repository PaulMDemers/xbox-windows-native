# 677 Launcher source pins reconciled

The four mismatches reported by 676 came from commit
`c05553b9fb3a954534876ca98f0a8a2b39031136`: the reviewed 480p sources changed,
but the launcher manifest retained its earlier four hashes and reference tree.
Current adapter/native/profile C and profile header bytes exactly match retained
633 source/build records. No maintained source file was edited in this review.

`promotion001.json` records all five manifest replacements, old/new manifest
hashes, unchanged default build flags and strict verification of all eight
profiles. New reference tree: `70c0a6c5aff82537f489e7d18410d5980fa797a7`.
No `--allow-modified`, missing-pin waiver or tree-comparison relaxation was used.

## Evidence

- `validation001.json`: sanitizer profile tests passed 129 checks; adapter
  tests passed 235,552 modeled assertions. Existing 720p/1080i tables and the
  retained 480p facts matched. Reconstruction then FAILED on `/mnt/c`.
- `tree-difference001.json`: all 244 differences were executable-mode changes;
  no blob contents differed. This failure remains intact.
- `validation002.json`: fresh Linux-filesystem source reconstructions both
  strictly matched the complete 633 tree. Default 720p and explicit 480p builds
  passed using the pinned GCC 12. Compiler-output identities are in the receipt.
- `wrapper001.json`: six compiled wrapper function fixtures passed: two modes
  times adapter results success, unsupported and partial failure. Requests,
  geometry, legacy fallback and reset/halt behavior were checked. Adapter
  results and reset operations are modeled, not physical operations.
- Strict `tools/xwn.py verify` passed all eight profiles; all 14 tests in
  `tests/test_xwn.py` passed after the manifest update.

Default remains 720p. Explicit 480p still requires a separate build selection.
No new binary was installed, and equality to the installed baseline is not
claimed. These checks do not fix boot intermittency or qualify another revision.

Private build outputs remain in `C:/xwn677` and
`/home/paul/xbox-windows-native/launcher677-validation002`. Build/test processes
finished and the build lease was released. Historical 633/676 records unchanged.

Next: [678 host-only diagnostic integration](../timer678/REPORT.md).
