# Hardware handoff after emulator qualification

First require candidate-eligibility.json from qualify-candidate.py. It validates
the same driver across stress001, independent stress002 and the original full
fifteen-minute mapping/BMP soak004, with all reports and evidence hashes intact.
The eligibility result permits planning a controlled trial; it is not a claim
that the console has passed or that the earlier physical strict failure is fixed.

Latest human Proceed was accepted as readiness following the keyboard-unplug
request. One physical trial is now recorded in ../fatx0101-physical; inspect its
stage records and never launch a duplicate. Xromwell can hang with the Razer
keyboard attached; preserve this constraint for future launches.

Refresh the read-only installed baseline and normal-startup checks before any
deployment. Preserve exact0098 and startup bytes locally and in the trial's own
rollback location. Keep video0093, boot-chain payloads, original0088 rollback,
the0.1.0 tag and recovery archives. Use a unique recorded launch and readback-verify
every staged payload. Never infer completion from dashboard availability alone.

Physical device setup needs a separate observation on its actual hardware. The
read-only snapshot at../physical-pnp-followup identifies incomplete GPU binding
and a latest unsupported audio installer, but historical PCI registry entries
are not a live bus inventory. The xemu-only1B36:0005 null INF is not a physical
APU/SMBus driver. Do not copy its policy to the console or force restart while
the installer queue is pending. Keep setup observations distinct from driver
and application-save qualification.

After a bounded driver trial returns, restore normal startup first, preserve
all before/after reports, and cold-check exact files, event deltas, full FATX
allocation, binaries and structural hives using the existing owned procedures.
Only then progress to the physical long soak and actual Paint save/reopen tests.
The three prior Srv2013 events and shutdown popup remain strict failures until
addressed with evidence. Do not create a new PASS-gated recovery bundle from an
emulator pass or silently relax event gates.
