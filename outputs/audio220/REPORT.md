# Physical Xbox audio trial completed

The experimental ACI driver passed genuine installation and a subsequent playback
boot on the physical Xbox. The captured incoming baseline is restored, dashboard identity was confirmed
before release, and the audio queue ticket is closed. USB may proceed.
No owned physical session remains active. Audible sound is still unconfirmed.

| Gate | Physical result |
| --- | --- |
| Genuine installation | PASS: one exact ACI target, UpdateDriver success, xwnaci207 service, no device problem. |
| Subsequent boot | PASS: started device, one xwnaci207 module, no ac97xnt5 module, one WinMM render device. |
| Playback/reset workload | PASS: twelve cycles; eight full two-second buffers and four reset-shortened cycles; full positions exactly 96,000 samples. |
| Normal restart | PASS on both Windows boots: joined helpers, unforced restart, one new EventLog6006 and dashboard return each. |
| Cold integrity | PASS on both boots: five valid hives, protected bytes, preserved event/setup history, selected policy unchanged, no new disabling, zero FATX allocation errors/orphans. |
| Restoration | PASS: 1,202 file readback checks; original startup, captured hive/companion/INF state and original audio driver restored; final allocation and dashboard checks passed. |
| Audible output | UNVERIFIED: no user observation or physical audio capture received. |
| Strict whole-boot qualification | FAIL: Ftdisk49 on both Windows boots remains unresolved. |

## Exact candidate and installation conditions

Driver version 0.0.4.207 targets only ACI PCI10DE:01B1, subsystem00000000,
revisionB1. Driver SHA256:
`c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
The reviewed source/package commit is `7cdb191bd2ef72e24001370726f97a7383a7250b`.
No driver-source or binary changes were made for this hardware trial.

A fresh read-only snapshot preserved 1,223 files, including all 1,175 incoming INF
entries. Five structural hive checks, 11 actual NT5 provider hashes and three
native export tables passed, including the physical Xbox HAL. The incoming ACI
service was ac97xnt5 with original driver SHA256
`9cccf729317efb34b1350c12ca2cc9b285fa57a8746147b93632bb1cce177efa`.

The trial matched the emulator installation starting condition: build004 bytes
temporarily replaced that legacy audio file before the first boot, without an
offline binding edit. Windows SetupAPI then genuinely installed xwnaci207 from the
exact-ID INF. The subsequent playback boot made no reinstall or binding changes.
Restoration later put the actual captured physical hives and original files back;
no emulator hive or fabricated binding was copied to the console.

## Restoration and retained evidence

Eleven changed files were restored and three precisely identified new files were
removed after their bytes were preserved. Event logs and SetupAPI history were
retained. The final allocation scan found 6,193 directories, 122,554 files, zero
errors and zero orphan clusters. A final read-only connection rechecked critical
baseline bytes, INF inventory and dashboard ownership before releasing the ticket.

The inactive trial directories remain as preserved evidence:
`/F/xwna220i`, `/F/xwna220p`, and the three E Applications folders
`XWNA220scanI`, `XWNA220scanP`, `XWNA220scanR`. Normal startup invokes none of them.
FATX0101/video0093, original0088 rollback and immutable0.1.0 were not replaced.

The first capture failed only on a host JSON-journal sharing error; its partial
snapshot is retained. A fresh capture completed after bounded save retries. An
initial host audit incorrectly required one target-count entry even though the
installer enumerates before and after UpdateDriver. The original false verdict
is retained; audit002 requires both successful checks and identical target IDs
against the same preserved evidence. No guest was relaunched to obtain a pass.
A pre-execution audit-adapter generator failure is also retained.

## Scope and next step

Known unrelated wizard cancellation was recorded, so these are not prompt-free
boot results. APU01B0 remains unsupported. Actual audible stereo, S/PDIF/HDMI
adapter output, capture, hardware mixer controls and protected-content playback
remain unqualified. API completion and sample counts do not prove audible sound.
The next audio-specific evidence needed is an actual output/connection observation.
Any new physical trial requires a newly coordinated ticket; this ticket is closed.

No HAL/kernel/video source or payload was changed. ACI uses its translated MMIO
aperture (observed FEC00000, size0x180), PortCls interrupt resource (observed IRQ6)
and ordinary DMA allocation. No GPU register/context operation was introduced.
Compatibility with future exploratory video layouts or accelerated GPU ownership
is not established by these audio tests.

## Records

- `install001/audit002.json`: corrected installation verdict; original audit retained.
- `playback001/audit.json`: physical device/module/playback and cold verdict.
- `restored001/restoration.json`, `confirmation.json`, `allocation.json`: restoration proof.
- `capture002.json` and private `artifacts/before002/`: complete fresh rollback inputs.
- `frozen001.json`, `frozen002.json`, `final-review001.json`: exact input/evidence reviews.
- `queue-close.json`: persistent restored-baseline release.
- `audibility.json`: explicitly unobserved output, not a negative sound report.

Source and reports are confined to branch `codex/xbox-native-audio`. Publication
verification is recorded separately after pushing. There was no main-branch merge,
release-tag change or deployment of an exploratory video candidate.
