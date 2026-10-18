# Host-only busy-state correction

51 executions of the actual assembled marker and51 immutable repeated calls
passed. All32 prior cases remain;19 additions cover physical469's0x0808 prefix,
host-only busy0x0008,both busy bits,busy-plus-done,persistent busy,time limits,
busy-plus-error/unknown,both transactions and both LED patterns. I/O/CLI/TSC
remain explicit host models. No hardware completion is inferred from modeled
future success after the captured prefix.

Only four assembly operands change: the two known-status masks and the two
busy-wait masks. Reverting these reconstructs exact465. The global4096-read and
64,000,000-tick budgets are unchanged. Tests assert no I/O writes while either
busy bit is set, no success on busy-plus-done, and refusal on error/unknown bits.
No retry,reset,error acknowledgment,EEPROM operation or status clearing added.

Private capsule C:/xwn470/host001 contains compiler-pinned source,executable,
disassembly,log and51 records. No XBE built,installed or launched. No physical,
emulator,Windows reliability,D3D or GPU result is claimed.
