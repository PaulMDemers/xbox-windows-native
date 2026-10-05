# Video diagnostics and repeated boots

The original 0.1.0 miniport includes a one-shot file logger. It expects a 4096-byte
file at SystemRoot/System32/xwn-video-trace.bin, a 16-byte marker, and all remaining
bytes zero. Reusing its populated output deliberately stops at
E0580001(0D,4,C000003E,10). Physical GDI 002 confirmed this exact guard with a
41-record trace. It was a harness reseed omission, not evidence of new FATX
corruption. Physical GDI 003 passed after preserving and reseeding that file.

Compile-time diagnostic switches are not independent in this historical driver.
XBOX_NT5_VIDEO_TRACE also selects PnP START forwarding instead of an intentional
checkpoint stop, and installs an unload wrapper. Simply disabling that flag is
not equivalent to disabling logging. Preserve the qualified callback behavior
when isolating diagnostic overhead.

Candidate 0092 retained the callbacks but replaced all trace hooks with no-ops.
That removed file I/O and diagnostic PCI reads. It passed two ordinary boots in
the private synthetic-resource xemu model, with GDI checks and normal shutdown,
but failed on hardware with STOP 0xB4 before the workload. The original miniport
was restored and verified. The experiment does not identify whether PCI reads,
file-I/O side effects, timing, or another difference matters. Do not conclude that
Windows inherently requires logging, or that xemu reproduces this hardware case.

Candidate 0093 branches directly from the qualified baseline. It retains those
operations and changes only how valid prior trace contents are initialized:
after length/marker validation, reset records in memory for the new boot. Host
reseeding should therefore be unnecessary for an intact installed trace. It
still requires the file and retains explicit guards for missing/invalid files
and I/O failures. See ../video-trace-reuse for actual qualification; source intent
is not itself proof of physical success.

For repeat-boot trials, preserve the used trace and launch records, use separate
exclusive workload logs, and require two normal shutdowns without host reseeding.
Check new event-log boundaries independently of old crash records. Keep the
captured release driver and a verified rollback copy. A failed hardware trial
must remain a failure even when the corresponding emulator report passed.

Performance work must stay separate from this maintenance fix. Physical GDI 003
identified much slower reads/overlapping screen copies than fills/uploads in a
bounded 256x128 workload. It did not measure dragging FPS or establish the cause.
Cache attributes and aliases, copy routines, and GPU ownership still require
their own review before changing rendering behavior.

## Shutdown-event comparison

Candidate0093 completed two ordinary boots with valid traces, pixel checks,
unchanged payloads and normal EventLog stops. Its strict no-popup audit failed on
rundll32 DLL initialization during window-station shutdown. A second two-boot
run added 30 seconds before shutdown and produced the same popup. Both failed
strict reports are retained; a longer delay did not fix it.

The captured-driver and reconstructed-driver controls each completed one clean
run. Those two negative observations do not establish that the popup is new:
the earlier qualified `native-windows-paint-save/matched-emulator-validation.json`
contains exactly the same message with the original miniport hash, before0093.
Its matching file audit verifies both original video and qualified FATX hashes.
Candidate and baseline SetupAPI logs also show the same unresolved device
installation, but this does not prove which process launched at shutdown.

`video-trace-reuse-settled/historical-assessment.json` makes the separate decision
to permit a bounded reversible hardware trial with that intermittent baseline
limitation recorded. All other correctness/error gates remain required, and the
physical audit still rejects any new popup. The strict emulator audits are not
rewritten or described as clean. The popup's mechanism remains unresolved.

The later clean-start two-boot series passed the full strict emulator audit with
no popup. That strict result—not the historical exception assessment—was used
for physical promotion. Both physical boots then passed without a trace reset
between them. See video-trace-reuse-settled/qualification.json; candidate0093 is
installed with normal startup restored. The existing file remains required.

## Later mapping investigation

0094 recorded the physical desktop aperture's first/last PTEs and CPU PAT/MTRRs:
UC mapping, with the known loader alias endpoints absent. Its GDI and normal
shutdown checks passed, but two identical rundll32 shutdown popups made its
strict physical audit false.0093 was restored and independently hash-verified.

0095's RAM address was rejected by VideoPortMapMemory in xemu (stage7/error87).
0096 owns an MmNonCached RAM mapping instead and passes compiled lifetime tests
and ordinary emulator pixel/actual-PTE checks. Both30-second and120-second
settling runs still failed the strict popup gate. None was promoted or deployed.
Stop/removal/restart ownership remains implementation work beyond the helper's
normal unmap/unload paths. The separate debugger run is exploratory; see
../video-shutdown-probe. Failure to capture a hard-error call does not identify
or exclude the popup's cause. Do not keep increasing waits or select a clean
retry as proof that timing fixed this issue.
