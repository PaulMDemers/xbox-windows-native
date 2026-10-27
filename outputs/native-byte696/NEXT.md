# Next after696: bounded native Xcalibur register read

696 is CLOSED. User reported a green held result; reviewed success predicate
requires cable byte1 and final known busy/terminal flags clear. No photo/raw native
capture for this run. User manually power-cycled; eight records twice matched,
local hashes verified, last persisted phase handoff_armed. Staged files and
unrelated entries match. Incoming1.6 is at HDMI UnleashX. No normal shutdown claim.
Read REPORT.md, analysis001.json and review001.json. Never rerun/recollect696.

1. Prepare a fresh native read-only encoder probe, using the checked handoff and
   independent display checkpoint. Audit the existing xcal_read32 protocol and
   source pins before transplanting it. Retain current platform/configuration,
   PCI identity/mapping, CPU and per-transaction entry gates; a historical pass
   cannot substitute for an admission check required by the new path.
2. Start with a bounded register read, not an initialization recipe or mode change.
   Require exactly the expected block length before reading data. Treat done+error
   as failure. Retain raw status/data/phase, acknowledge only owned observed
   terminal bits, and check final status. Timeout never retries or clears unknown
   inherited status. Do not characterize a returned value as a unique encoder ID
   without independently supported semantics.
3. Keep persistent visible stages and raw results independent of SMBus LED writes.
   Prove code/GDT/IDT/context/stack bounds before adding code:696 code1111, GDT4c0,
   pointers end4f6, input500, context540, final shadow580..5a0, IO data5a0..5c8,
   IDT600..e00, stacke00..1000. Do not exceed a layout limit to avoid a rebuild.
4. Use new actual-linked CPU and IO fixtures, including bad lengths, errors,
   timeout, ownership, late completion and final status. Keep model/device claims
   separate. Preserve every failure and exact frozen source/binary/attributes.
5. Stage a unique owned E/F path with readback, get current watch/reset availability,
   and issue one20-second-bound SITE request. Never retry acceptance/uncertainty.
   Record observation, manual recovery and exact collection before closing.

No next candidate built/staged. No startup hook or owned host process. All ten696
VMs closed; hardware ticket retained, build/emulator leases released, automation
paused. Preserve build001's short-color-table defect and io-review001 pixel
failure; build002's table correction passed all33 IO models. Prior695 photo
calibration failure and all earlier evidence remain intact. Networking679,1080i
and historical boot intermittency remain tabled. Original720p/ordinary launcher
unchanged; no Windows1.6, native initialization or accelerated capability claim.
