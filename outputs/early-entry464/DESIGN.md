# Requirements for a bounded early-entry discriminator

Preserve original installed720p launcher and all prior diagnostics. A successor
must retain462's first-refusal file before the original paging transition, using
a new exclusive namespace. Missing files remain unknown. No Xbox kernel/file
services are callable after the paging transition.

Use distinct evidence classes for pre-transition readiness, entry to the physical
copied loader, arrival at relocated Cromwell, and established private stack.
An entry marker before0x026000f5 must be stackless or establish a separately proven
private stack without destroying original live registers. A post-stack marker
must preserve registers/flags, copied span bounds, GDT/IDT and original control
flow. The marker must not survive by using arbitrary borrowed/reserved memory.
Any changed embedded payload, branch target or relocated copy needs independent
byte reconstruction and copy verification;462's unchanged payload proof cannot
be inherited by name.

Front-panel LEDs are a possible independent observation channel, not persistent
storage. Existing helpers are rejected unchanged: busy/completion loops are
unbounded, failure is discarded, and the wrapper debug loop is terminal. A new
adapter must bound both waits and the entire transaction count, distinguish busy,
NACK/error, pending and acknowledged completion, and avoid blind retries or bus
reset. Bound by poll counts as well as an appropriate measured timer; poll counts
alone do not promise a wall-clock duration. Preserve exact partial-transaction
state and define refusal without falsely claiming a displayed marker.

Do not program unrelated SMC registers, EEPROM, flash, disk sectors, video mode,
firmware channels, or a global reset to obtain persistence. Do not infer missing
LED evidence means entry was not reached. Dashboard restart may replace an LED
pattern; a short-lived pattern needs external observation rather than an FTP
collector pretending it persisted. A visible debug halt would be a separate
explicitly bounded diagnostic, not ordinary boot or reliability evidence.

Before any physical candidate: test actual generated code register/stack/control
flow preservation, copy limits and every bounded status/partial-write path;
validate the new execution boundary on a fresh owned emulator fixture. Emulator
SMC models remain separate from physical acknowledgments. Then prepare one fresh
watched console attempt with a documented recovery and collection sequence.
