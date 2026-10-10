#226 ownership reducer and matched backend source review

Implemented the serialized producer/drain/private-context/submission/restore
transition in `owner.c`, with immutable copied ranges, paired operation receipts,
a single finite budget and terminal quarantine after exposure. This is portable
implementation for a future NT5 adapter; it performs no GPU writes and grants no
native ownership. The actual225 state still refuses preparation because its
full old-owner census, backing and backend/context services are unknown.

The matched xemu source review establishes why existing idle, shutdown and
flush signals cannot fill those gaps. OpenGL shutdown only waits shader cache;
Vulkan shutdown hooks are empty. OpenGL surface flush invalidates surfaces
while its all-dirty download is commented out. FIFO idle can mean a blocked
worker. No emulator modification was made or launched.

`host001.json` records368513 assertions at each of O0/O2 under ASan/UBSan:
4096 synthetic complete cycles,100000 inherited-range overlap refusals,100000
private-range overlap refusals, paired/stale receipts, wrong-channel context,
missing retirement obligations and bounded failure/cancellation paths. The same
reducer compiles to an import-free i686 object with the pinned RosBE compiler.
This qualifies host ordering/range behavior and compile compatibility only.

`inventory001.json` pins12 exact compiled-model sources and closed225 evidence.
The entire20KiB inherited aperture is protected; RAMFC/RAMRO decoded fields are
retained without guessing extents. Details and the adapter store obligations are
in DESIGN.md. Ordinary emulator execution, physical validation, backend drain,
context service and GPU acceleration remain unqualified for this implementation.

All226 commands are closed; no guest, observer or hardware launch exists. C:
20GiB build guard remains unchanged. Source/repository review and publication
are recorded separately; Git HEAD/origin/main are publication authority.
