# 691 loader allocation preflight — safely refused, closed

One kernel preflight returned automatically according to its restart record and
subsequent dashboard collection. All eight reports read back twice identically.
A later user reply reports a red top and dashboard return, but692 had launched
before that reply. Both runs recorded refusal; unique visual attribution remains
uncertain. See observation001.json.

The source buffer was allocated at physical01f00000 with size00100000 and all
pages verified. The legacy-style stub request supplied highest address02000000;
the kernel returned a4096-byte allocation beginning exactly at02000000. The
preflight requires the complete page below02000000 and therefore refused it.
It did not query that page's continuity, call NtAllocateVirtualMemory, copy the
canary or transition to native code. The zero stub_contiguous field means NOT
CHECKED, not discontiguous. Virtual status ffffffff is a sentinel, not an error
returned by the kernel. Refusal bits6 combine the stub-range refusal with the
unattempted virtual stage. Both contiguous allocations were freed.

This is a diagnostic request/guard boundary mismatch, not a kernel allocator
bug, memory corruption or proof of689's native failure. The next fresh probe
will request a highest address of01ffffff while retaining the same guard.
The extra SDK framebuffer also changes allocation state relative to689; these
are fresh kernel preflights, not replays of that closed runtime.

## Executed host evidence

Five fresh Unicorn cases execute the retained689 XBE wrapper up to transfer with
modeled kernel APIs. A successful exact mapping reaches transfer. Null source
and null stub allocations reach MmGetPhysicalAddress(NULL). A virtual allocation
failure reaches a low-address write without ownership; a rounded returned base
reaches a relocated-pointer write outside the owned high stub page. These confirm
unchecked failure paths in the compiled wrapper under the supplied models; none
of those conditions is established on hardware by691. The actual required stub
extent through its GDT descriptor is226 bytes, within the1024 bytes copied.

The first model attempt failed on a Python memory-hook callback signature and
is retained. Corrected fresh002 passed. Sanitizer policy tests cover failures,
overlap and12285 unaligned cases;15 actual nxdk-object cases passed. Neither
executes the real kernel allocator or the paging transition. The physical probe
uses the actual kernel and records admission before any canary copy.

One SITE launch was accepted at00:44:24 UTC October27. There was no retry, native
handoff, SMBus transaction, startup hook, console C access or ordinary launcher
change. SDK mode setup uses kernel services with no application-enforced timeout.
Staged files and unrelated directory entries matched; this is not whole-volume
health proof. All invoked fixtures and this runtime are CLOSED; do not rerun or
recollect them. No owned host process or build lease remains; hardware ticket
retained. Incoming1.6 last verified at the HDMI dashboard. Owned E files retained.

See [compiled-wrapper models](legacy-audit002.json),
[initial harness failure](legacy-audit001.json), [build](build001.json),
[sanitizers](host001.json), [object cases](object-review001.json),
[review](review001.json), [launch](launch001.json),
[collection](collection001.json), [analysis](analysis001.json),
[closure](closure001.json), and [next](NEXT.md).
