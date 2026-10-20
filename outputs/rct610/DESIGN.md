# PC610 original DLL lifetime qualification

The PC609 game recorder rejected an unload after all 536 observed calls returned.
This attempt tests original code only. No closed runtime is reused or modified.

Each loaded module gets a monotonic generation. Active image ranges cannot
overlap. Breakpoints belong to one generation; retired entries remain historical
and cannot intercept new code or supply an old instruction byte.

Unload admission is read-only and requires a known active module, no pending
calls anywhere, no single-step or held threads, and only disabled, disarmed,
unreferenced return sites in the unloading image with matching ownership.
Entry sites, conflicting ownership and inconsistent state fail closed. Only
after the complete check passes are those records retired and the module marked
inactive. Unload never reads or writes the departing image.

Two small original DLLs use the same preferred base and return-site layout with
different harmless instruction bytes (NOP versus CLC). The subject loads A, B,
then A, calls each, checks its result and the restored return byte, and unloads.
Actual base/address reuse is measured and required for this control; it is not
assumed from link addresses. Pristine and traced outputs must agree exactly.
The earlier graphics, recursion, phase and absent-output controls remain enabled.

Shared admission code gets host tests for unsafe states before a fresh immutable
404 child boots. An independent trace parser checks generation, retirement,
pairing and code bytes, with adversarial trace mutations. Normal restart, cold
tool/OS/seed and hive/event checks close the fixture. Models alone do not qualify
NT5 debug-event order. This is neither a game result nor a performance result.
