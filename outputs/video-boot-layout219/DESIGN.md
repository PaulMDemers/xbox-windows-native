# Boot-video writable layout219

The permanent four MiB UC mapping currently contains both visible pixels and
indexed boot-video backing. Physical query218 found passive correspondence for
the top20KiB GPU instance window beneath64KiB stock query padding. The old indexed
buffer overlaps this window, and ResetDisplay clears the entire mapping.

Keep the allocation, UC mapping, provider reference ownership and shared ABI
unchanged. Limit boot-video writes to the lower0x3eb000 bytes. Place the fixed
316160-byte indexed backing at relative0x39dd00, ending immediately before the
protected0x15000-byte tail. Validate visible width/height before multiplication;
reject a visible surface that overlaps indexed backing. Publish the new backing
offset through the existing provider contract and clear only WritableBytes.

For64MiB the writable domain ends03feb000; indexed storage is03f9dd00..03feb000.
The03feb000..04000000 tail stays outside boot-video clear/pixel storage. The same
relative exclusion is conservative on128MiB: no physical UMA transform or GPU
capacity is inferred from that host arithmetic test.

This change does not establish GPU context ownership, coherent PRAMIN access,
DMA/cache handoff, working acceleration or additional supported video modes.
Host guarded calls use actual extracted drawing function bodies with modeled
HAL/font/palette wrappers; they cannot substitute for boot initialization and
actual reset/crash rendering. Ordinary emulator GDI/cold audits are separate
from a later sacrificial live guard test. No physical driver is changed here.

Build001 recompiles the actual control and candidate bootvid translation units
with the pinned compiler and pefixup. It reuses pinned supporting objects,
resources and import archives from the verified106 provider build. This is a
matched rebuild, not a full clean reconstruction of all native sources.

Two standalone cold children derive from the actual211 emulator fixture, with
only the219 boot provider and fresh diagnostic namespace/startup helper staged.
The inherited physical-core device policy is retained; inherited_null_policy is
false. The unchanged211 miniport lacks216 GPU snapshot hooks, so the derived
audit explicitly does not require those unrelated packets. All actual GDI,
setup-idle, event, integrity, shutdown and dashboard gates remain in force.

Read-only HMP observations never stop the CPU or seed a guard. Initial observer
uses an old fixed kernel address; observer002 uses the retained two-IDT-gate
kernel discovery after that address was inaccessible. Both source versions and
separate output records are preserved. These reads establish only actual module
identity and stable layout values if successful; they prove no general memory
coherence or complete runtime write exclusion.
