# 732: measured CR22 read-plane model and first-mismatch recorder

CLOSED host-only, 2026-10-27. No console access, stage, launch, XBE or functional
mode-switch change. Console remains last observed at UnleashX after731.

## Finding

Physical731 measured CR22 FE/E7/5A/FF for GR04 planes0/1/2/3; three reads per
plane agreed. Those are observed read values in that kernel-context run, not a
universal reset state or proof of CR22 write effects. The original phase4 code
writes CR22 FF and requires FF on readback before initializing GR04 in phase7.

We freshly rebuilt unchanged704 source with pinned GCC12; its instruction image
matches704 build004. Source-only reuse from730 supplied the harness scaffolding;
no closed runtime, fixture, image or binary was reused. C output and WSL backing
volume passed a projected20.05GiB reserve check, with about63GB free on each check.

48 fresh isolated executions combine four initial read planes, three expressly
hypothetical CR22 write behaviors, and four failure conditions. Each instance
starts with the measured731 read values. Under ignored writes, planes0/1/2 reject
at CR22 and plane3 accepts phase4. Under selected-latch or all-latch writes, all
four otherwise-successful cases accept. These policies are counterfactuals, not
claims about NV2A. Earlier MMIO or CR1b mismatches stop before CR22; a CR33 mismatch
is reached only when preceding checks pass. There are9 accepts and39 rejects.
Successful cases stop BEFORE geometry; rejected cases execute original reblank
and selector restoration. No encoder, later modesetting or framebuffer draw runs.

This demonstrates why substituting FE for FF, or choosing plane3 just to pass,
cannot qualify the original mode switch. It does not identify708/709's failure.
Source review also finds phase7 sets GR04=0 before repeating check_setup. If an
ignored-write/unchanged-latch hypothesis held that far, a plane3 phase4 pass would
not guarantee later acceptance. Later phases were NOT dynamically executed here.

## RAM-only recorder

transaction732.c differs from transaction003.c only by replacing check_setup
with the same ordered reads and predicates plus a separate volatile RAM trace.
It records magic0732, after_geometry, completed count, first mismatch, and up to
17 entries: register offset, CRTC index or FFFFFFFF, expected value, actual value.
Each actual value comes from the original read, never a second hardware read.
It preserves the first mismatch and returns rejection immediately. No changed
register write, added selector read, forced plane, mask or validation waiver.
The rest of the transaction source is byte-for-byte equivalent as decoded text.

A second fresh build and48 fresh isolated executions test the recorder. Offline
independent assertions check every captured entry against the ordered setup
contract and injected failure. All48 cases have identical register/port traces,
result prefixes and pass/fail outcomes to their unchanged-code counterparts.
This validates the recorder in the host harness, not its physical timing or a
physical display path. RAM writes and instruction timing are necessarily added.
The full transaction still contains the original writes; this candidate is not
a read-only hardware probe and is not approved here for physical execution.

## Evidence and limits

- build001.json/build002.json: compiler, command, space and executable hashes.
- model001.json/model002.json: every read/write, hypothetical policy and result.
- audit001.json:48 differential comparisons and independent first-mismatch checks.
- source-reuse001.json: exact retained source and physical evidence identities.
- sources001.json: initial build/model freeze; sources002.json: complete authored kit.

No compile/model/audit failure occurred. All96 isolated executions finished;
leases released, no owned process/VM/hook. No proprietary firmware was acquired
or interpreted. Ordinary720p, launchers, Windows and protected configuration are
unchanged. All earlier failed and closed attempts remain preserved. See
CAPTURE-PLAN.md for the physical admission work still required.
