# RAM0109 explicit ownership: emulator qualification PASS

All three guest attempts are CLOSED. Do not relaunch/recollect them. No physical access.

The foreign-PDEV dereference and handle-only shadow substitution in RAM0108 are
replaced by explicit live primary/PDEV/HDEV membership. Unknown device surfaces
and mixed owned PDEVs fail before Eng rendering. The 32-entry membership semaphore
is released before rendering, upload or resource callbacks. Registration failure
fully unwinds surface creation. See DESIGN.md for GDI lifetime assumptions and limits.

Source tree: `1f5aa1cee2bf9b4ca03e5581a8536db9c11db3d2`.
DLL: `ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440`.
Patch 0109 follows 0108; all compiled display sources and owned NT5 imports verified.

Host checks: 46 source lifecycle/render cases, 65,536 ROP dependency truth tables,
7 additional rejection/unwind cases and 80,000 concurrent registry cycles across 8 threads.
ASan/UBSan/leak checks pass. A PROT_NONE foreign private pointer was never read.
Reentrant ownership lookup from engine stubs completed with no table lock held.
These are host API shims, not real Windows multi-device or teardown concurrency proof.

## Ordinary matched pair

- control001: strict PASS, 54 cases/162 GDI pixel stages; normal shutdown count 1 and dashboard return.
  Callback counts: `[10628, 47421, 65, 0, 0, 0, 0, 0, 0, 4, 0, 2, 11, 1]`; upload bytes: 757928952.
- candidate001: strict PASS, 54 cases/162 GDI pixel stages; normal shutdown count 1 and dashboard return.
  Callback counts: `[9560, 48481, 65, 0, 0, 0, 0, 0, 0, 4, 0, 2, 11, 1]`; upload bytes: 807095708.

Both runs pass 54 full-visible driver coherence checks, full allocation, 5 structural
hives, all protected/payload hashes, zero new warning/error/application events,
unchanged 96 MiB/1,536-cluster pagefile and permanent UC shared mapping. Both fixtures
contain identical old/new driver payloads. Only one expected-driver byte and two
display selectors differ; all other logical SYSTEM nodes/values unchanged.

## Independent diagnostic

video-ownership-scanout/candidate001: strict diagnostic PASS, 12 physical frames/
1794048 RGB pixels, zero mismatches; 261 runtime pins including all
11668 relocated display.text bytes. Complete breakpoint teardown and resume.
Same 54 cases, 162 pixel stages, coherence, cold storage and event gates pass. This is explicitly not an ordinary run.
Raw emulator framebuffer captures and exact hashes are preserved privately under artifacts/.

## Boundaries and next work

This closes the ownership change and initial copy-path regression, not all 14 DDIs,
cursor exclusion, mode/bootvid/crash handling, multiple active displays or Xbox speed.
No physical deployment. Keep physical 0101/video0093, 0088 rollback, immutable 0.1.0
and qualified 128 GiB recovery unchanged. Original 111-byte non-ASCII physical corruption
and first-restart mechanism remain unresolved.

Next: real GDI vector/text/mask/clip/alpha cases against a DIB reference and raw
physical scanout, then cursor/lifecycle/crash checks. See NEXT.md.

Draft-source001 preserves the generator assertion of 27 versus 25 replacements; it was never compiled.
Earlier failed scanout observers remain failed in their original immutable kits.
All source snapshots, guest disks and immutable backing chains verified.
