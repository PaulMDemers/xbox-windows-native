# Next: design the late write-combining transition

All current cases are CLOSED. Never relaunch/recollect video-shared-trace001,
video-shared-trace2/trace002 or video-shared-crash/crash001. The first observer
failure is retained separately; the narrowed alias diagnostic and controlled
crash checks passed. See their reports and exact JSON records. The ordinary0106
pair remains the functional baseline; no new driver build in these diagnostics.

The mapping remains UC. Inspect the actual owned NT5 cache/mapping primitives
before choosing the transition implementation. Early boot's WC allocation was
already shown to fail while MiWriteCombiningPtes=0; do not flip that private flag.
At desktop acquisition, require a reviewed protocol for boot/error drawing,
consumer references, every alias, cache flush and TLB synchronization. Counted
references and InbvCheckDisplayOwnership are insufficient for exclusivity.

The critical failure case is a crash or allocation failure between retiring the
UC mapping and publishing WC. Define a valid renderer address and bounded rollback
for every state before coding; do not keep conflicting UC/WC aliases as a shortcut.
If supported NT5 primitives cannot meet this, document that result and revisit
the shadow-surface design instead of patching private kernel PTE state blindly.
Use matched fresh UC/WC children, exact GDI correctness, alias/cache evidence,
normal shutdown/cold gates and sacrificial crash validation before physical work.

No physical deployment/testing authorized by this diagnostic step. Preserve
physical0101/video0093,0088rollback,immutable0.1.0,completed128GiB recovery and all
failures. Original111nonASCIIphysical corruption remains unresolved. Old
automationPAUSED. Cfree22832881664bytes at closure;20GiB build guard unchanged.
