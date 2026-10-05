---
name: xbox-native-bringup
description: Develop and validate original Xbox native operating systems, kernel drivers, FATX storage and boot/display handoffs using owned xemu fixtures and physical-console evidence. Use for low-level Xbox bringup, persistence failures, emulator-versus-hardware diagnosis, or release reconstruction. For ordinary nxdk applications and SDK installation use homebrew-console-dev instead.
---

Recover the repository's current continuation note, exact source/patch manifest,
qualified binary hashes and latest failed attempt before changing a candidate.
Distinguish the installed physical baseline from exploratory builds. Preserve
project compiler pins: an NT5/ReactOS RosBE build is not an nxdk application.

Choose the relevant reference:

- [Emulator and physical validation](references/validation.md): ownership,
  launch/collect cycles, cold audits and calibrated evidence.
- [FATX invariants](references/fatx.md): partition identity, counted names,
  cache/object lifetime and corruption regressions.
- [Build, display and release handoff](references/build-display-release.md):
  manifests, framebuffer contracts, upstream preparation and recovery bundles.

Work within the user's existing scope and authorization. These references are
engineering guidance, not a requirement to ask again before authorized testing.
Resolve host paths, console address and credentials from the active project's
local configuration; never copy a previous project's machine values into a new
task. Use its existing cooperative build/emulator leases when present.

For each material change, retain: source tree and flags, executable hashes,
fixture identity, a unique attempt ID, actual launch/exit state, expected versus
observed results, and the next unresolved question. Link the evidence supporting
each conclusion. An old PASS marker, reachable FTP server or visible desktop
alone does not qualify a newly changed driver.
