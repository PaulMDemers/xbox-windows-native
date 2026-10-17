# Logged preparation followed by the original handoff

This is a new diagnostic, not a boot fix. The installed launcher stays unchanged.
Derive the wrapper from its pinned original source and preserve its exact embedded
Cromwell payload, original allocation parameters, two 1024-byte copies and loader.
An isolated XBE will use a new exclusive report under E:\Applications\XWNBoot460a.
The embedded loader still uses the original XWNEBoot chain.

At the original final jump, save all eight general registers and EFLAGS. Verify
the payload, both copied loaders and far-jump targets. Record these facts before
the paging transition. Require exact synchronous create/write/flush/close results;
then recheck all three copies after logging, restore the saved state and execute
the original jump. Failures return to the dashboard without attempting handoff.
No kernel/file call is added after CLI or paging changes. No test startup hook.

The 176-byte report contains a 160-byte version2 header and16-byte trailer.
The eight saved words at128 are PUSHAD order: EDI,ESI,EBP,ESP-after-PUSHFD,
EBX,EDX,ECX,EAX. Flags are at112;120 marks a valid snapshot and124 eligibility
before file I/O. A full report is NOT evidence that final flush, close, the fresh
copy recheck or the jump succeeded. The diagnostic changes timing and allocations.
Individual kernel file calls have no independent cancellation guarantee.

Before any console stage, execute the assembled wrapper in a32-bit host harness
with explicitly modeled kernel/file operations. Trap the first privileged CLI
at the copied loader rather than execute paging changes; compare restored CPU
state to the saved frame. Exercise copy, mapping, status, short-I/O, close and
post-log corruption failures. Independently decode captures and reject mutations.
Host success is not physical handoff evidence. A console launch is a separate,
unique attempt, with exact staging/readback and collection after dashboard return.
