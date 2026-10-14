# Builds and provenance

Exact source trees, tool hashes, definitions and evidence are recorded. A
clean-machine, one-command build of the complete current E demo is not yet ready.

| Component | Current lineage |
|---|---|
| FATX | candidate0101 |
| HD reservation, miniport, boot video | reservation300 |
| Software display | video303 |
| E boot chain | stock-boot334; E720p launcher resolution-e374 |
| Audio | ACI207 build004 |
| Drag preference utility | demo-settings376 (corrected parser), original MIT code; installed folder remains xwndemo372 |

The [reconstruction prototype](../outputs/reproducible-build/README.md) describes
its explicit limits. Its older `all` profile does not build the current combined
HD/audio/E stack. New experimental binaries are not automatically promoted.

Public builds need parameterized paths, pinned upstream revisions and ordered
patches, and a per-component license inventory. ReactOS, Cromwell, nxdk-derived
code and original tools retain their respective notices. The outline utility's
license does not cover unrelated code.

Build in fresh source/output directories under the shared resource lease; do
not alter SDK/input fixtures. Preserve the 20 GiB reserve, failed logs and exact
commands. Review NT5 imports before guest execution. Compilation is not runtime
qualification.

Windows media, firmware, EEPROM, dashboards and user profiles are local inputs,
not public assets. Reconstruct the current stack twice from empty output
directories and explain binary differences before claiming determinism.
Reproducible ZIP assembly alone is not a full compiler rebuild.
