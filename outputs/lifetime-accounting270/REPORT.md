#270: bounded lifecycle accounting passed host validation

The proposed observer accounting now keeps first binds and final frees in
dedicated generation records, separate from repeated nonfinal events. Exact
run-length records retain ordering and pre-decrement counts; saturation remains
a strict failure. No renderer integration or new guest launch occurred.

The127 captured269 callbacks reconstruct exactly from seven runs and one reserved
first-bind record. All129 original event files were verified against their
existing hashes. An external-incomplete marker still rejects that historical
input:269 remains failed and its later lifetimes remain unknown.

ASan/UBSan host validation passed1,000,730 checks, including one million repeated
decrements, independent full-sequence reconstruction, four final frees, reused
addresses/stale generations, bounded run/counter/sequence exhaustion and reserved
lifecycle capture after saturation. The exact existing one-word gate passed4096
publication races with the new accounting state, plus busy, foreign-owner and
closed-entry refusals. Both compilations were warning-free. Private frozen inputs
and binaries are at E:/Codex-archive/xbox-windows-native/lifetime270-host001.

The installed nxdk mesh and triangle sources were reviewed for a deterministic
owned graphics control. They offer actual guest allocation/draw paths, but neither
already covers four unchanged textures across disable/checkpoint/re-enable.
WORKLOAD.md records the concrete control, including separate standalone ownership,
required attestation, independent texture/framebuffer oracles and finite waits.
The old color-bars launcher is not ready: its referenced configuration is absent.

Physical audio004/softwarevideo118/shared158/FATX0101 and all recovery/release
baselines remain unchanged. No GPU grant, disposal, ordinary/performance result or
physical promotion follows from this host component.269 and every prior failure
are preserved; inherited Ftdisk49 remains a strict event failure.
