# Development workflow

Start with the [source map](../src/README.md) and [build guide](building.md).
Change the smallest relevant component. Keep source revisions, compiler settings,
output hashes and test scope together. Profiles remain separate until a combined
source tree is deliberately built and qualified.

## Editing a profile

1. Run `python3 tools/xwn.py verify` on the baseline.
2. Edit the actual file in `src/`. Preserve upstream notices.
3. Build into a fresh directory with `--allow-modified` for existing listed files.
   New files, deletions and mode changes need explicit manifest updates.
4. Inspect build logs and the recorded tree/artifact hashes. Do not equate a
   successful build with binary reproducibility or deployment readiness.
5. Add a test that distinguishes the intended behavior from the defect. Prefer
   a disposable emulator fixture before a physical trial.
6. Preserve the failed attempt and its inputs; use a new attempt for corrections.

Use `python3 tests/test_xwn.py` for the portable command's guard tests and
`python3 tools/check-repository.py` for tracked payload/credential checks. On
shared development machines, acquire the existing build/emulator/hardware lease
and coordinate ownership before using those resources.

## Evidence levels

Host models prove only their modeled contracts. A debugger observation is not an
ordinary guest run; a synthetic API replay is not a user exercising Paint.
An emulator result is not physical-console qualification. Record what actually
ran, where, with which source and binaries, and what remains uncertain.

For persistence changes, verify exact final contents, absent intermediate files,
allocation consistency, relevant hives/protected files, shutdown and event deltas.
Never turn a scoped success into a strict pass by suppressing failed event gates.
A clean metadata audit alone is not a full file-content comparison.

For graphics, separate guest framebuffer contents from displayed output. Require
actual ownership, synchronization and content preservation before experiments
that release renderer resources or hand control to a new GPU path. The emulator
resource-lifetime experiments are not installed native acceleration.

## Before public release

Finish the complete HAL/network/input source inventory, verify anonymous upstream
and toolchain acquisition, validate builds in a clean environment, and qualify a
disposable owned-media installer and restore. Review per-component licensing and
corresponding source, then export a curated tree without private history or data.
Do not publish the historical `outputs/` directory wholesale.

Historical evidence remains in `outputs/`. New users should not need machine
paths, experiment IDs or private archives to understand the project. Maintain the
public guides separately from immutable test records.
