# Wait for both controller busy bits

Physical469 captured0x0808 after starting transaction0. Pinned Linux nForce
controller source identifies bit3 as host-busy and bit11 as bus-busy. This new
host-only marker changes exactly four assembly operands: accept0x0008 as known
and wait while either busy bit is set, in both idle and completion loops.

Busy is never success. Even busy plus completion waits; no configuration or
acknowledgment is issued while either busy bit is set. Abort,collision,protocol,
timeout and unknown bits still refuse before any busy wait. Existing4096-read
and64,000,000-tick limits, no retry/reset and register/flag preservation remain.
Only idle completion0x10 is acknowledged. The source reconstructs exact465 by
reverting those four operands. Old467/469 refusals remain failures.

The host adds19 cases to all32 inherited cases: both busy bits separately and
together, busy-plus-completion, persistent busy budgets, busy-plus-error/unknown,
clock expiry, both transactions and both LED patterns. Privileged I/O/TSC are
modeled. No wrapper integration, XBE build, emulator/physical test or boot fix is
claimed by this kit. New integration needs updated strict failure parsing and
the full refusal snapshot retained. Do not edit any previously executed kit.
