# 467: physical LED diagnostic deliberately refused before handoff

The user watched one launch at2026-10-18T00:43:20.952578Z and reported:
"Amber, the screen changed but stayed black and exited". Dashboard FTP returned
at00:43:43.840994Z. There was no second launch or automatic retry.

The complete primary preparation report passed its copy/mapping checks. The
separate complete refusal record identifies reason12, bounded first-marker
refusal, with marker result5: the helper observed status bits outside its allowed
busy/completed mask. The primary report had already closed successfully. The
wrapper took its deliberate refusal path before the original privileged loader;
this trial does not reproduce or explain the original intermittent launcher
failure. The second marker was not reached through that path.

The exact raw SMBus status, transaction index, count and started/completed mask
were only in volatile marker memory and were not persisted by this build. They
remain UNKNOWN. Amber is the user's observation; it does not independently
prove two acknowledged transactions. Do not infer an electrical fault, relax
the status gate or turn this refusal into a boot-success claim.

The staged537170-byte XBE matches466build001 SHA256
74a479078f378b8f02c54d4bd146765a7d860031116f636a3658a6616c2bedf5.
It resides only in E:\Applications\XWNBoot466a beside the original launcher.
Collection read every file twice. Original launcher/startup, five hives, two
event logs and video trace are byte-identical before/after. The owner receipt and
candidate also match. Protected720p baseline verification passed before staging,
before launch and on collection. Console C was not accessed. No startup hook,
driver, SDK or physical baseline was changed. Raw captures remain private at
C:/xwn467/physical001.

cold-review001 failed at module import because the existing offline hive library
directory was absent from the process loader path. Its source and failure are
retained. Fresh cold-review002 uses that existing directory explicitly; no
dependency installation or console operation was performed by the correction.

This trial is CLOSED after collection. Preserve all receipts and never reuse its
directory or accepted launch. Next work is a separate, host-tested way to append
the complete first-marker record on the already-selected refusal path, while the
kernel stack and file services are still valid. No new physical test is queued.
