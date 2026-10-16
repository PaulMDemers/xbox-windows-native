# Tester rollout plan

## First: inventory, without Windows installation

Use the utilities preview to collect kernel, RAM, PCI, AV-pack and encoder
observations. Corrected preview 421 completed on the development console and
returned a report; obsolete 417/417b builds must not be used. Start with one
coordinated inventory run on each other configuration. Keep reports associated
with the exact XBE/ZIP hash; this does not qualify Windows on that configuration.

| Configuration | Current Windows evidence | Initial tester action |
|---|---|---|
| Known 64 MiB Conexant configuration | Existing E/720p demo works; clean rebuild still needs physical confirmation | Inventory, then matched preview after boot-chain test |
| Other Conexant consoles / BIOSes | Not individually qualified | Inventory and boot-profile review |
| Focus | Not qualified | Inventory only before display/boot review |
| Xcalibur or unidentified encoder | Not qualified | Inventory only; do not infer an encoder from missing responses |
| RAM-upgraded or nonstandard partition layout | Not generally qualified | Inventory and explicit configuration review |

## Then: qualify one Windows package

1. Complete the staged rebuilt-loader comparison on the development console.
   Use the same direct File Explorer route and record normal restart and rollback.
2. Resolve the six overlong paths in the clean-media assembly without silently
   discarding Windows state. Record any explicitly supported exclusions and their
   functional tests; keep the original strict failure visible.
3. Parameterize provisioning from the validated user-owned installation input.
   Require a matched E/720p launcher, loader, HAL, drivers and registry. Keep the
   original Windows image and a complete path/hash ledger.
4. Create a new private preview with the bundle planner. Record uncompressed size,
   free-space reserve, media SHA-256, source commit, each binary and hive hash,
   normal startup, known issues, and expected mapping. Review private data before
   sharing; a hash manifest is not a sanitizer or redistribution permission.
5. Exercise install, direct boot, document persistence, audio/video, normal restart,
   second boot and removal/restore on a fresh disposable standard-size image.
   Follow with the same sequence on hardware, protecting dashboard C.
6. Give one matched preview to one suitable tester per configuration first. Expand
   only after a report explains the launch route, display and restart behavior.

## Keep package results distinct

Inventory success does not establish Windows compatibility. Compilation does not
prove bootability. The 720p demo, rebuilt clean-media candidate and 1080i experiment
are different configurations. Preserve the Ftdisk/event and FATX-transfer failures
until resolved; do not silently turn them into a clean-release PASS.

Deliverables are a small public utilities kit, open-source component/build tools,
and a locally assembled Windows preview using the tester's own appropriate media.
Do not use the developer's private recovery archive as the public Windows package.
The first broader Windows release remains gated by the work above.
