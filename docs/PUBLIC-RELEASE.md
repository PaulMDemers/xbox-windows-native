# First public source release

Status: preparation. No visibility change, upload, history rewrite or new tag
has been performed for this demo.

Prefer a fresh, reviewed source export while preserving private forensic
history and recovery archives. Changing this repository's visibility directly
would expose all reachable history.

Include current guides, exact upstream pins/patches, parameterized build and
configuration tools, focused tests, bounded evidence, component licenses and an
artifact manifest. Exclude the wholesale `outputs` tree, Windows/firmware/EEPROM/
dashboard files, hives, private pixels, user data, credentials and recovery ZIPs.

## Remaining gates

| Gate | Evidence needed |
|---|---|
| Provenance | License and upstream revision for every distributed component |
| Build | Fresh reconstruction of the current boot/storage/video/audio stack |
| Modes | Explicit E/F targeting, rollback/readback and truthful qualification labels |
| Installer | Disposable-fixture validation of the corrected create-only flow |
| Content | Allowlisted export reviewed for private data, secrets, media and local paths |
| Claims | Hardware/emulator/user observations distinct; failed event gates visible |
| Recovery | Tested rollback documented; no claim of an untested full restore |
| Publication | Review final source commit and every archive entry before publishing |

`tools/check-repository.py` checks tracked payload exclusions and credential
patterns. `tools/audit-public-readiness.py` inventories history without printing
matched secrets. Neither establishes license/privacy clearance. Inspect the
actual export and retain original attribution.

Existing private tags remain immutable. Choose the public release identity after
the exported contents and configuration tools are ready.
