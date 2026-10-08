# First CPU write to an unread GPU surface passed

The single144 run passed all16 exact full-buffer readbacks, including the stronger
first-write case. After the initial GPU readback, the GPU clears to a different
background. Without any intervening CPU read, the CPU overwrites a small rectangle
17 times. The following readback must retain the new GPU background outside that
rectangle. A subsequent overlapping GPU clear must retain the CPU pixels outside
its bounds, followed by a full GPU clear and another CPU readback.

This passed for linear A8R8G8B8 color and Z24S8 depth/stencil, in two pbkit lifetimes:
19,660,800 exact readback bytes and120,292 volatile CPU stores. The trace shows the
expected additional first-write downloads: eight downloads per surface versus six
in143. Color has three uploads and depth four before first invalidation. Complete
transfer order, dimensions, pitch, binding and bytes per pixel are checked.

The same two surface addresses survive pbkit teardown/reinitialization. Later
invalidation and recreation are observed during dashboard handoff. No explicit
emulator-device reset, overlapping-watch race, Z16 or swizzled coverage is claimed.

Cold audit: all18 expected new files, no unexpected new files, unchanged existing E
file contents/chains, clean E allocation, and no top-overlay ranges anywhere in F.
The immutable backing chain is unchanged. The probe requested a normal reboot;
the observer saw FTP go offline and return to the dashboard. This observer uses
offline collection and makes no FTP data-transfer attempt, preserving the earlier
transport failures as separate evidence.

Launch15:49:47 UTC, dashboard15:50:09, cleanup15:50:10 on October8,2026. All owned
sessions are closed. Same pinned xemu binary and SDK libraries; no Windows drivers,
physical console, service policy or guest cache settings changed. No debugger was
used. Sparse trace timings are not performance evidence, and this is not a qualified
xemu optimization.

The corpus now provides both read-first and write-first CPU/GPU coherence controls.
It is suitable for testing a proposed watch lifetime change, alongside explicit
reset/overlap coverage and the existing Windows correctness/performance workloads.
