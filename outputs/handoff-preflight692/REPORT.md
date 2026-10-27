# 692 rounded virtual reservation observed — safely refused, closed

The new stub upper-limit request01ffffff kept its entire page below32MiB. The
source occupied01f00000..02000000 and the stub01eff000..01f00000; both allocations
passed metadata and page checks. NtAllocateVirtualMemory returned success but
changed the requested base01eff000 to01ef0000 and expanded size4096 to65536.
The offset is61440, leaving exactly4096 bytes at the requested address.

The exact-base guard refused that change (bit4). No alias translation, canary
copy or native transition occurred. The returned virtual allocation was released
successfully using its returned base; source and stub were freed. All eight
reports were read back twice, including restart_requested/complete. Dashboard
returned and staged bytes/unrelated directory entries matched.

This is actual kernel evidence of an in/out address mutation that the old XBE
wrapper does not preserve separately. [691's compiled-wrapper models](../handoff-preflight691/legacy-audit002.json)
show an unsafe pointer write when that mutation is supplied to its unchecked
path. It is a concrete candidate loader defect, not proof of the exact689 failure
or the historical intermittent-boot cause. The kernel is allowed to return a
rounded reservation; the diagnostic must distinguish that base from its original
physical execution target. The added SDK framebuffer changes the allocation state
relative to689, so this is not a replay of that runtime.

The user reported dashboard return and a red top in response to691's question,
after692 had also launched. Both records independently command a red header;
unique visual attribution is uncertain. No native display qualification follows.

The sole runtime delta from691 after namespace normalization was the upper-limit
argument. Sanitizer cases and16 nxdk-object cases passed; the32MiB boundary remains
rejected. The retained source comment about matching legacy requests refers to
the shape, not the deliberately changed upper limit. One SITE launch accepted
at00:49:28 UTC October27, no retry. No hook, console C access, native transfer,
SMBus read or ordinary launcher change. SDK services lack application deadlines.
All invoked fixtures and this runtime CLOSED. No owned host process/build lease;
hardware ticket retained, owned E files retained. No whole-volume health claim.

Evidence: [build](build001.json), [sanitizers](host001.json),
[object cases](object-review001.json), [delta review](review001.json),
[launch](launch001.json), [collection](collection001.json),
[analysis](analysis001.json), [user observation](observation001.json),
[closure](closure001.json), [next](NEXT.md).
