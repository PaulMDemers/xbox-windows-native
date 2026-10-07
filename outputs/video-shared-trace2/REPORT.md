# Shared UC alias and ownership diagnostic passed

trace002 is CLOSED and diagnostic PASS. The observer captured six paired calls
in24 stops: one direct-RAM4MiB MmMapIoSpace request with cache argument0,
successful publication, two display-ownership-loss notifications, successful
provider acquisition, and its InbvCheckDisplayOwnership return0. Thread, return
address and callee stack cleanup match for every pair.219 resident byte pins
include the entire bootvid and miniport text sections.

At the first drawing marker, the published view, acquire output and bootvid
FrameBufferStart all equal FCED6000, mapping physical03C00000. Ready=1,
References=1 and Owner matches the acquiring miniport. The hidden backbuffer
translates to the expected reserved-RAM offset. The snapshot contains20 linked
active processes/page-table roots. Every root has exactly one4MiB framebuffer
mapping through1024 supervisor4KiB PTEs, with PCD/PWT=1 and PAT=0. No mapping of
the F3C00000 aperture remains. Before this change each root had two mappings.

This is a present-page snapshot, not TLB, inactive/future-root or live MSR proof.
No cache policy was changed and no speed claim follows from debugger timing.
All breakpoints were removed before continuing.54drawing cases/162pixel checks,
normal restart/dashboard, full F allocation324dirs6755files325directory clusters
with0errors/orphans,5hives/protected hashes, configuration/pagefile and strict
event gates passed. No new warning/error/application events. No physical access.

See verification.json for compact ranges and pins; alias-scan.json and RAM stay
private. The preceding video-shared-trace/trace001 remains a recorded observer
failure; its resumed guest also passed the cold gates. No cases were relaunched.
Preparation15410,runner64258,tracer67262,supervisor12320,audit44905 all CLOSED.
Next separate sacrificial crash is in video-shared-crash; WC remains unimplemented.
