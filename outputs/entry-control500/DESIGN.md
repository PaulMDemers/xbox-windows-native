# Bounded controller for the unlaunched499 entry candidate

This kit adds stage/launch/observe/collect orchestration for exact499, whose
SHA256 is22d3a9224965159a53cb188be9530f1b211aff8480d3d5773405d7e2974cf6d9.
It creates only a fresh E:\Applications\XWNBoot499a directory, owner.json and
default.xbe. It never changes the ordinary launcher, mode, drivers, startup or
dashboard C. Existing demo251 hardware ownership and protected720p checks remain.
It does not build a new XBE or create a Windows workload/startup hook.

Before staging, ten protected/mutable files are read twice and preserved. Launch
requires the exact candidate/owner and every before-file hash unchanged, a clean
known startup listing and no preexisting receipt. Requested intent is saved BEFORE
one SITE request with a20-second reply bound. A saved request, uncertain response
or supervisor action record prevents another launch. No automatic retry exists.

Five fixed receipts are supported: entry, report, refusal, handoff and context.
Only the new entry transport is decoded here; legacy receipts are preserved raw
for their independent existing decoders. Directory listings distinguish absence
from a listed-but-unreadable file. A listed550 is a read failure, never absence.
Receipt listing and transfer sizes are both capped4096bytes, paths are fixed and
unknown contents in the owned directory refuse. Paired cold reads detect changes.
Only transient transfer operations may retry on a fresh connection, at most twice;
SITE requests and completed/partial collection attempts never retry.

The independent498 decoder distinguishes absent/malformed/complete entry. A
complete receipt does not establish final flush/close, preparation or Windows
startup. The same complete bytes can remain after final-I/O failure. An absent
file does not prove the XBE failed to enter. Actual provenance must include fresh
staging, exact candidate and unchanged collected inputs; host-model receipts
are never physical evidence. Cold collection records normal-Windows-shutdown as
unproved until a separate hive/event audit establishes it.

The new supervise002.py owns exactly one child per action. Stage180s, launch90s,
observation240s and collection240s are outer host limits; the inner observation
window is180s. It records the action before spawning, uses the existing tested260
bounded atomic JSON writer, terminates only its child on timeout, and records
whether the process closed. This cannot cancel a console boot or prove console
shutdown. A timed-out launch remains uncertain; partial staging/collection remains
preserved. Use this supervisor, never an unbounded direct physical.py invocation.

supervise.py/ supervisor-host001 are retained prototypes using one-shot local
replace. Production002 reuses260's bounded sharing recovery. Both supervisor
tests execute real success, failure and timeout child processes, then refuse
repeated actions. They do not access FTP or Xbox. No sleep child remains running.

host001 executes32 actual controller paths with FTP, baseline, ownership and time
explicitly modeled. It covers acceptance/uncertainty, stale state, protected input
changes, all five preexisting receipts, partial stage, bounded transfers, paired
read mismatch, complete/short/corrupt/absent receipts, current observation deadlines
and no request/collection retry. Package verification itself runs with actual
candidate/source hashes; the hardware ownership interface is modeled in this test.

RETURN PLAN: exact499 proceeds into the old Windows boot after successful entry
I/O. This kit intentionally has no automatic Windows restart. It must not be
launched without an explicit plan for a potentially running desktop. An operator
normal restart is one option. For unattended work, prepare a NEW reviewed kit
that either (a) returns after the entry observation using a tested continuation,
or (b) installs a unique bounded Windows runner for the already-PC-qualified496
scene, with tested hook-first cleanup. Neither is implemented by500. The pending
497 screen history can remain unknown; it is not an additional permission gate
for independently justified new diagnostics. It must never be invented or used
to justify an identical retry of the closed497 launch.
