# Both markers wait for host and bus busy

Integrate exact470 into both marker positions in exact468, retaining the complete
192-byte refusal capture and original handoff. A new471 namespace prevents old
reports from being reused. The original payload before its owned tail is exact;
only four instruction operand bytes in that tail change. The wrapper core has
the same four operand changes; all source reconstructs the exact predecessor.
No callback, driver, SDK, normal launcher or startup change.

Known host/bus busy bits0x0008/0x0800 cause bounded waiting, never success. Busy
plus completion waits; error or unknown bits refuse. Existing poll/timestamp
bounds, acknowledgment rules and no retry/reset are retained. A successful
marker only advances original boot diagnosis. Historical boot reliability is
not established by a diagnostic or debugger run.

Host actual-wrapper and post-stack execution must cover the captured469 prefix,
both markers, error/file failures and unchanged register/stack/flag contracts.
Fresh owned emulator validates actual loaded bytes and original continuation,
then bounded cleanup and full cold audit. Physical use is separately recorded.
